# -*- encoding: utf-8 -*-
# author: yxin

from io import BytesIO
import os,aiofiles,re,sys
from pathlib import Path as FilePath
import openpyxl
from PyPDF4 import PdfFileMerger
from loguru import logger
from config import appConfig
from fastapi import APIRouter, Body, Path, UploadFile, File
from fastapi import Response as FResponse
from fastapi.responses import StreamingResponse
from typing import Optional
from model import Response
from model.invoiceModel import InvoiceCreateModel, InvoiceUpdateModel, InvoiceList, InvoiceQueryParams,InvoiceDetailModel
from dao.invoiceDao import InvoiceDao
from dao.purchaserDao import PurchaserDao
from invoiceParser import pdfParser

router = APIRouter()
invoiceDao = InvoiceDao()
purchaserDao = PurchaserDao()

class InvoiceListResponse(Response):
    invoices: Optional[InvoiceList] = None

class InvoiceDetailResponse(Response):
    invoice: Optional[InvoiceDetailModel] = None

def checkPurchaser(invoice: InvoiceCreateModel) -> bool:
    purchasers = purchaserDao.list()
    # 没有添加抬头，则不校验抬头
    if not purchasers.purchaserList:
        return True
    for purchaser in purchasers.purchaserList:
        if purchaser.name and re.sub('[\(\)（）-]','',purchaser.name) == re.sub('[\(\)（）-]','',invoice.purchaserName):
            if purchaser.taxNumber and purchaser.taxNumber == invoice.purchaserTaxNumber:
                return True
            elif not purchaser.taxNumber:
                return True 
    return False

@router.get("/{id}", response_model=InvoiceDetailResponse)
async def getInvoice(id: str = Path(..., title='id of invoice', regex="^\w{25}$")):
    response = InvoiceDetailResponse()
    response.invoice = invoiceDao.queryById(id)
    return response

@router.post("/list", response_model=InvoiceListResponse)
async def list(queryParams: InvoiceQueryParams = Body(...)):
    response = InvoiceListResponse()
    response.invoices = invoiceDao.list(queryParams)
    return response


@router.delete("/{id}", response_model=Response)
async def delete(id: str = Path(..., title='ids of invoice', regex="^\w{25}(,\w{25})*$")):
    return invoiceDao.delete(id)

@router.get("/status/{status}/{id}", response_model=Response)
async def updateStatus(status: str = Path(..., regex="^[0|1]$"), id: str = Path(..., title='ids of invoice', regex="^\w{25}(,\w{25})*$")):
    return invoiceDao.updateStatus(status, id)

@router.get("/feetype/{feeType}/{id}", response_model=Response)
async def updateFeeType(feeType: str = Path(..., regex="^\S+$"), id: str = Path(..., title='ids of invoice', regex="^\w{25}(,\w{25})*$")):
    return invoiceDao.updateFeeType(feeType, id)

# 新增发票
@router.post("/", response_model=Response) 
async def add(invoice: InvoiceCreateModel = Body(...)):
    invoice.purchaserTaxNumber = invoice.purchaserTaxNumber.upper()
    if not checkPurchaser(invoice):
        return Response(code=500, message='抬头不匹配，请确认抬头是否正确，或在设置中添加抬头')
    invoice.totalAmount = int(round(invoice.totalAmount*100))
    invoice.totalTax = int(round(invoice.totalTax*100))
    invoice.taxRate = int(round(invoice.taxRate*100))
    invoice.total = int(round(invoice.total*100))
    return invoiceDao.add(invoice)

# 更新发票
@router.put("/{id}", response_model=Response)
async def update(id: str = Path(..., title='id of invoice', regex="^\w{25}$"), invoice: InvoiceUpdateModel = Body(...)):
    invoice.totalAmount = int(round(invoice.totalAmount*100))
    invoice.totalTax = int(round(invoice.totalTax*100))
    invoice.taxRate = int(round(invoice.taxRate*100))
    invoice.total = int(round(invoice.total*100))
    invoice.id = id
    return invoiceDao.update(invoice)

# 上传发票文件
@router.post("/import", response_model=Response, status_code=500)
async def upload(file: UploadFile = File(..., description="文件"), response: FResponse = FResponse()):
    try:
        filename = file.filename
        if not filename.endswith('.pdf'):
            return Response(code=500, message='文件类型错误')

        # 保存发票文件
        filetype = filename.split('.')[-1]
        filename = filename.replace('.','').replace(filetype, '')
        saveName = FilePath(appConfig.uploadPath, f'{filename}.{filetype}')
        rename = 1
        while os.path.exists(saveName):
            saveName = FilePath(appConfig.uploadPath, f'{filename}_{rename}.{filetype}')
            rename += 1
        async with aiofiles.open(saveName, 'wb') as f:
            await f.write(await file.read())

        # 解析发票文件
        invoice = pdfParser.read_invoice(saveName)
        # 校验抬头
        if not checkPurchaser(invoice):
            os.remove(saveName)
            return Response(code=500, message='抬头不匹配，请确认抬头是否正确，或在设置中添加抬头')
        # 保存到数据库
        if invoice.number and invoice.purchaserName and invoice.total>0:
            invoice.totalAmount = int(round(invoice.totalAmount*100))
            invoice.totalTax = int(round(invoice.totalTax*100))
            invoice.taxRate = int(round(invoice.taxRate*100))
            invoice.total = int(round(invoice.total*100))
            invoice.date = invoice.date.replace('年', '-').replace('月', '-').replace('日', '')
            res = invoiceDao.add(invoice, saveName.__str__(),'1')
            # 如果存储数据库失败，删除文件
            if res.code != 200:
                os.remove(saveName)
                return res
        else:
            os.remove(saveName)
            return Response(code=500, message='发票文件解析失败')
        
        response.status_code = 200
        return Response(code=200, message='发票导入成功')
    except Exception as e:
        logger.error(e)
        if saveName and os.path.exists(saveName):
            os.remove(saveName)
        return Response(code=500, message='发票导入错误')

# 导出excel
@router.get("/exportexcel/{id}")
async def exportExcel(id: str = Path(..., title='ids of invoice', regex="^\w{25}(,\w{25})*$")):
    invoices = invoiceDao.queryByIds(id)
    output = BytesIO()
    workbook = openpyxl.Workbook()
    sheet=workbook[workbook.sheetnames[0]]
    # 导出开票日期、发票代码、发票号码、校验码、购买方名称和税号、销售方名称和税号、价格、税率、税额、价税合计、备注
    sheet.append(['开票日期','发票代码','发票号码','校验码','购买方名称','购买方税号','销售方名称','销售方税号','价格','税率','税额','价税合计','备注'])
    for invoice in invoices.invoiceList:
        sheet.append([invoice.date,invoice.code,invoice.number,invoice.checkCode,invoice.purchaserName,invoice.purchaserTaxNumber,invoice.sellerName,invoice.sellerTaxNumber,invoice.totalAmount,invoice.taxRate,invoice.totalTax,invoice.total,invoice.remark])
    workbook.save(output)
    workbook.close()
    output.seek(0)
    headers = {
        'Content-Disposition': 'attachment; filename="fapiao.xlsx"'
    }
    return StreamingResponse(output, headers=headers)

# 导出pdf
@router.get("/exportpdf/{id}")
async def exportPdf(id: str = Path(..., title='ids of invoice', regex="^\w{25}(,\w{25})*$")):
    invoices = invoiceDao.queryByIds(id)
    output = BytesIO()
    try:
        merger = PdfFileMerger()
        for invoice in invoices.invoiceList:
            if invoice.filePath:
                merger.append(invoice.filePath)
        merger.write(output)
        merger.close()
        output.seek(0)
        headers = {
            'Content-Disposition': 'attachment; filename="fapiao.pdf"'
        }
        return StreamingResponse(output, headers=headers)
    except Exception as e:
        logger.error(e)
        logger.error('合并pdf失败', e)
        return('合并pdf失败')

