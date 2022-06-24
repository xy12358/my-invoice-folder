# -*- encoding: utf-8 -*-
from random import randint
import uuid
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime
from model import Base, Page
from pydantic import BaseModel, Field
from typing import List, Optional

def key():
    # mac后4位+时间戳+4位随机数
    return f"{uuid.UUID(int=uuid.getnode()).hex[-4:]}{(datetime.now()).strftime('%Y%m%d%H%M%S%f')[:-3]}{randint(1000, 9999)}"

class InvoiceModel(Base):
    __tablename__ = 'invoce'
    id = Column(String(32), primary_key=True, default=key, comment="发票id")
    type = Column(String(64), nullable=False, comment="发票类型")
    number = Column(String(16), nullable=False, comment="发票号码")
    date = Column(String(8), nullable=False, comment="开票日期")
    machineNumber = Column(String(16), comment="机器编号")
    code = Column(String(16), comment="发票代码")
    checkCode = Column(String(32), comment="校验码")
    payee = Column(String(32), comment="收款人")
    reviewer = Column(String(32), comment="复核")
    drawer = Column(String(32), comment="开票人")
    purchaserName = Column(String(128), nullable=False, comment="购买方名称")
    purchaserTaxNumber = Column(String(32), comment="纳税人识别号")
    purchaserAddress = Column(String(256), comment="地址电话")
    purchaserBank = Column(String(256), comment="开户行及账号")
    password = Column(String(128), comment="密码")
    serviceType = Column(String(128), comment="项目类型")
    totalAmount = Column(Integer, comment="合计金额")
    totalTax = Column(Integer, comment="合计税额")
    taxRate = Column(Integer, comment="税率")
    total = Column(Integer, comment="价税合计")
    sellerName = Column(String(128), comment="销售方名称")
    sellerTaxNumber = Column(String(32), comment="纳税人识别号")
    sellerAddress = Column(String(256), comment="地址电话")
    sellerBank = Column(String(256), comment="开户行及账号")
    remark = Column(String(256), comment="备注")
    timestamp = Column(DateTime, default=datetime.now(), comment="时间戳")
    # 0未使用，1已使用
    used = Column(String(2), default="0", comment="是否已使用")
    feeType = Column(String(32), default="未分类", comment="费用类型")
    # 添加类型，0为手动添加，1为文件导入
    addType = Column(String(2), comment="添加类型", default="0")
    # 文件路径
    filePath = Column(String(256), comment="文件路径")

    def to_dict(self):
        dict = {}
        dict.update(self.__dict__)
        # 如果_sa_instance_state存在，则删除
        dict.pop('_sa_instance_state', None)
        # 格式化timestamp时间戳
        dict["timestamp"] = datetime.strftime(self.timestamp, "%Y-%m-%d") if self.timestamp else ""
        dict["totalAmount"] = round(self.totalAmount/100.0, 2) if self.totalAmount else 0
        dict["totalTax"] = round(self.totalTax/100.0, 2) if self.totalTax else 0
        dict["taxRate"] = round(self.taxRate/100.0, 2) if self.taxRate else 0
        dict["total"] = round(self.total/100.0, 2) if self.total else 0
        return dict
        
class InvoiceCreateModel(BaseModel):
    type: str = Field("普通发票", title="发票类型")
    number: str = Field("", title="发票号码", regex="^[0-9]*$")
    date: str = Field("", title="开票日期", regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    machineNumber: str = Field("", title="机器编号", regex="^[0-9]*$")
    code: str = Field("", title="发票代码", regex="^[0-9]*$")
    checkCode: str = Field("", title="校验码", regex="^[0-9]*$")
    payee: str = Field("", title="收款人")
    reviewer: str = Field("", title="复核")
    drawer: str = Field("", title="开票人")
    purchaserName: str = Field("", title="购买方名称")
    purchaserTaxNumber: str = Field("", title="纳税人识别号", regex="^[0-9]|[a-z]|[A-Z]*$")
    purchaserAddress: str = Field("", title="地址电话")
    purchaserBank: str = Field("", title="开户行及账号")
    password: str = Field("", title="密码")
    serviceType: str = Field("", title="项目类型")
    totalAmount: float = Field(0, title="合计金额")
    totalTax: float = Field(0, title="合计税额")
    taxRate: float = Field(0, title="税率")
    total: float = Field(0, title="价税合计")
    sellerName: str = Field("", title="销售方名称")
    sellerTaxNumber: str = Field("", title="纳税人识别号", regex="^[0-9]|[a-z]|[A-Z]*$")
    sellerAddress: str = Field("", title="地址电话")
    sellerBank: str = Field("", title="开户行及账号")
    remark: str = Field("", title="备注")
    feeType: str = Field("未分类", title="费用类型")
    used: str = Field("0", title="是否已使用")

class InvoiceUpdateModel(InvoiceCreateModel):
    id: str = Field(None, title="发票id", regex="^\w{25}$")

class InvoiceDetailModel(InvoiceUpdateModel):
    timestamp: str = Field(None, title="添加日期", regex="^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    addType: str = Field(None, title="添加类型", regex="^0|1$")
    filePath: str = Field(None, title="文件路径")


class InvoiceQueryModel(BaseModel):
    dateType: int = Field(0, title="日期类型(0:开票日期，1:添加日期)")
    startDate: str = Field(f'{datetime.now().year}-01', title="开始日期", regex="^[0-9]{4}-[0-9]{2}$")
    endDate: str = Field(f'{datetime.now().year+1}-01', title="结束日期", regex="^[0-9]{4}-[0-9]{2}$")
    purchaserName: str = Field("", title="购买方名称")
    used: str = Field("", title="是否已使用")
    feeType: List[str] = Field([], title="费用类型")


class InvoiceQueryParams(BaseModel):
    page: Optional[Page]
    query: Optional[InvoiceQueryModel]

class InvoiceList(InvoiceQueryParams):
    invoiceList: Optional[List[InvoiceDetailModel]] = []