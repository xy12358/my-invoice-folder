# -*- encoding: utf-8 -*-
# author: yxin

from random import randint
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from model import Base, Response
from pydantic import BaseModel, Field
from typing import List, Optional

def key():
    # mac后4位+时间戳+4位随机数
    return f"{uuid.UUID(int=uuid.getnode()).hex[-4:]}{(datetime.now()).strftime('%Y%m%d%H%M%S%f')[:-3]}{randint(1000, 9999)}"

class PurchaserModel(Base):
    __tablename__ = 'purchaser'
    id = Column(String(32), primary_key=True, default=key, comment="购买方id")
    name = Column(String(128), nullable=False, comment="购买方名称")
    taxNumber = Column(String(32), comment="纳税人识别号")
    address = Column(String(256), comment="地址")
    phone = Column(String(32), comment="联系电话")
    bankName = Column(String(256), comment="开户行")
    bankAccount = Column(String(32), comment="银行账号")
    timestamp = Column(DateTime, nullable=False, default=datetime.now(), comment="时间戳")

        
class PurchaserCreateModel(BaseModel):
    name: str = Field(..., title="购买方名称", max_length=100, regex="^\S{1,100}$")
    taxNumber: Optional[str] = Field('', title="纳税人识别号", regex="^.{0}$|^\w{18}$")
    address: Optional[str] = Field('', title="地址", max_length=100, regex="^.{0}$|^\S{1,100}$")
    phone: Optional[str] = Field('', title="联系电话", regex="^.{0}$|^0\d{2,3}-\d{6,8}$")
    bankName: Optional[str] = Field('', title="开户行", max_length=100, regex="^.{0}$|^\S{1,100}$")
    bankAccount: Optional[str] = Field('', title="银行账号", regex="^.{0}$|^\d{12,24}$")

class PurchaserUpdateModel(PurchaserCreateModel):
    id: str = Field(None, title="购买方id", regex="^\w{25}$")


class PurchaserListModel(Response):
    purchaserList: Optional[List[PurchaserUpdateModel]] = []