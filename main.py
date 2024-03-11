from fastapi import FastAPI,UploadFile,File,HTTPException,Request,Response
from fastapi.exception_handlers import RequestValidationError
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse,RedirectResponse,PlainTextResponse,HTMLResponse,JSONResponse
from typing import Dict
from fastapi.templating import Jinja2Templates
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#import pdb;pdb.set_trace()
#from model import Table,Intern,User,FileMetadata,Login
from model import Table,User,Login
from schema import User as UserModel
from typing import List,Optional
from jose import jwt,JWTError
import re, os, string ,pdfplumber,shutil,uvicorn
#import pdb;pdb.set_trace()
app=FastAPI()
#temapalates=Jinja2Templates(directory="tempalates")
temapalates=Jinja2Templates(directory=os.path.abspath(os.path.expanduser('templates')))
SQLALCHEMY_DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/postgres"
#SQLALCHEMY_URL="postgresql+psycopg2://postgres:postgres@localhost/testdb"
engine=create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

@app.get("/register",response_class=HTMLResponse)
def register_po(request:Request):
    #import pdb; pdb.set_trace()
    return temapalates.TemplateResponse("registration.html",{"request":request})


static_directory=os.path.join(os.path.dirname(os.path.abspath('tempalates')))
app.mount("/static",StaticFiles(directory="static"),name="static")

@app.post("/regpost",response_model=UserModel)
async def register(request:Request):
    session=SessionLocal()
    try:
        form= await request.form()
        username=form.get('username')
        password=form.get('password')
        email=form.get('email')
        try:
            existing_user=session.query(User).filter(User.email==email).first()
        except:
            existing_user=None
        if existing_user:
            raise HTTPException(status_code=400,detail="Email address not registered")
        new_user=User(username=username,email=email,password=password)
        session.add(new_user)
        session.commit()
        #session.refresh(new_user)
        return temapalates.TemplateResponse("login.html",{"request":request})
    except Exception as e:
        print(f"An error occurred:{e}")
        raise HTTPException(status_code=500,detail="Internal server error")
    finally:
        session.close()

static_directory=os.path.join(os.path.dirname(os.path.abspath('tempalates')))
#static_directory=os.path.join(os.path.dirname(os.path.abspath()),temapalates)
app.mount("/static",StaticFiles(directory="static"),name="static")
@app.get("/login",response_class=HTMLResponse)  
async def login_po(request:Request):
    return temapalates.TemplateResponse("login.html",{"request":request})

@app.get("/home",response_class=HTMLResponse)  
async def login_po(request:Request):
    return temapalates.TemplateResponse("home.html",{"request":request})


@app.get("/",response_class=HTMLResponse)  
async def login_po(request:Request):
    return temapalates.TemplateResponse("login.html",{"request":request})

@app.post("/login_post",response_class=HTMLResponse)
async def login(request:Request):
    session=None
    try:
        form= await request.form()
        
        # import pdb; pdb.set_trace()
        email=form.get('email')
        password=form.get('password')
        # email=form.get('email')
        #import pdb; pdb.set_trace()
        session=SessionLocal()
        user = session.query(User).filter(User.email==email).first()
        if user is None or user.password!=password:
            #raise HTTPException(status_code=401,detail="Invalid username or password")
            return temapalates.TemplateResponse("error.html",{"request":request,"status_code":"401","error":"Invalid username or password"})
        # login_session=Login(username=user.username,password=password)
        # session.add(login_session)
        # session.commit()
        return temapalates.TemplateResponse("home.html",{"request":request,"username":user.username})
        # event = {"id": 123}
        # # redirect_url = request.url_for('/home/', **{'pk': event['id']})
        # # redirect_url = request.url_for('/home')
        # response = RedirectResponse(url='/home')
        # return response
    except Exception as e:
        print(f"An error occured during login:{str(e)}")
        raise HTTPException(status_code=500,detail=f"An error occurred  during login:{str(e)}")
    finally:
        if session:
            session.close()

#static_directory=os.path.join(os.path.dirname(os.path.abspath()),temapalates)
static_directory=os.path.join(os.path.dirname(os.path.abspath('tempalates')))
app.mount("/static",StaticFiles(directory="static"),name="static")
@app.post("/pdf_search",response_class=HTMLResponse)
async def pdf_search(file:UploadFile,request:Request):
    session=SessionLocal()
    
    form= await request.form()
    keyword=form.get("keyword")
    keyword="test"
    try:
        with open("uploaded_pdf.pdf","wb")as buffer:
            buffer.write(await file.read())
            #buffer.write(file.read())
        extracted_words=set()
        with pdfplumber.open("uploaded_pdf.pdf") as pdf:
            for page in pdf.pages:
                page_text=page.extract_text()
                try:
                    page_text_split=page_text.split()
                except Exception as e:
                    print("Error splitting page text:",e)
                    continue
                for each_keyword in page_text_split:
                    if each_keyword==keyword:
                        table_entry=Table(name=keyword,text=keyword)    
                        session.add(table_entry)
                        session.commit()
                extracted_words.update(page_text_split)
        # import pdb;pdb.set_trace()
        # print("-----------------",extracted_words)
        result=[word for word in extracted_words if re.search(fr"\b{re.escape(keyword)}\b",word)]
        results="\n".join(result)
        return temapalates.TemplateResponse("upload.html",{"request":{},"keyword":keyword,"message":"is found" if keyword else "not found"})
    except Exception as e:
        print("-----------------",keyword)
        print(f"An error occurred during PDF search:{str(e)}")
        raise HTTPException(status_code=500,detail=f"An error occurred during PDF search:{str(e)}")
    finally:
        session.close()
      
@app.get("/upload",response_class=HTMLResponse)
async def uploadfile_po(request:Request):
    return temapalates.TemplateResponse("upload.html",{"request":request})
static_directory=os.path.join(os.path.dirname(os.path.abspath('tempalates')))
app.mount("/static",StaticFiles(directory="static"),name="static")



if __name__=="__main__":
    uvicorn.run(app,host='0.0.0.0',port=9001)                      


#python -m pip install fastapi uvicorn[standard]
#python -m pip install SQLAlchemy Flask-SQLAlchemy
#python -m pip install python-jose
#python -m pip install pdfplumber
#python -m pip install psycopg2
#https://www.educative.io/answers/how-to-use-postgresql-database-in-fastapi
