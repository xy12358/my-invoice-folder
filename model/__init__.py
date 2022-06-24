from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import appConfig
from pydantic import BaseModel
from fastapi import status

# 分页
class Page(BaseModel):
    currentPage: int = 1
    pageSize: int = 10
    totalRecords: int = 0
    totalPages: int = 0

class Response(BaseModel):
    code: int = status.HTTP_200_OK
    message: str = 'ok'

engine = create_engine(appConfig.database['url'], echo=appConfig.database['echo'])
Base = declarative_base(engine)
session = sessionmaker(bind=engine)()


    