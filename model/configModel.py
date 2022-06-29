# -*- encoding: utf-8 -*-
# author: yxin

from random import randint
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from model import Base
from pydantic import BaseModel
from typing import Optional

def key():
    # mac后4位+时间戳+4位随机数
    return f"{uuid.UUID(int=uuid.getnode()).hex[-4:]}{(datetime.now()).strftime('%Y%m%d%H%M%S%f')[:-3]}{randint(1000, 9999)}"

class ConfigModel(Base):
    __tablename__ = 'config'
    # id = Column(String(32), primary_key=True, default=key, comment="配置id")
    key = Column(String(100), primary_key=True, comment="配置名称")
    value = Column(String(500), nullable=False, comment="配置内容")
    description = Column(String(200), comment="备注")
    timestamp = Column(DateTime, default=datetime.now(), comment="时间戳")

class ConfigDetailModel(BaseModel):
    key: str
    value: str
    description: Optional[str]
        