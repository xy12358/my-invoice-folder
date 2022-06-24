from loguru import logger
import pdfplumber
from PyPDF4 import PdfFileMerger
import openpyxl
import re
from model.invoiceModel import InvoiceCreateModel, InvoiceDetailModel


# 解析PDF格式电子发票
def read_invoice(pdf_file: any) -> "InvoiceCreateModel":
    invoice = InvoiceCreateModel()
    try:
        with pdfplumber.open(pdf_file) as pdf:
            # 读取第一页
            first_page = pdf.pages[0]
            # 读取文本
            text = first_page.extract_text().replace(" ", "").replace(" ", "")
            # print(text)
            if '专用发票' in text:
                invoice.type = '专用发票'
            elif '普通发票' in text:
                invoice.type = '普通发票'
            else:
               raise Exception('未知发票类型或非发票文件')
            # 提取发票表格上方内容
            invoice.number = re.search(r'发票号码(:|：)(\d+)', text).group(2)
            invoice.date = re.search(r'开票日期(:|：)(.*)', text).group(2)
            invoice.machineNumber = re.search(r'机器编号(:|：)(\d+)', text).group(2)
            invoice.code = re.search(r'发票代码(:|：)(\d+)', text).group(2)
            invoice.checkCode = re.search(r'校验码(:|：)(\d+)', text).group(2)
            # 提取发票表格下方内容，全在一行里
            match = re.search(r'.*收款人(:|：)(.*)复核(:|：)(.*)开票人(:|：)(.*)销售', text)
            invoice.payee = match.group(2)
            invoice.reviewer = match.group(4)
            invoice.drawer = match.group(6)
            # 读取表格
            table = first_page.extract_table()
            # 表格为4行11列
            # ‘购买方’，内容，none,none,none,none,‘密码区’，密码,none,none,none
            # 货物名，none,规格，单位，数量，单价，none,none,金额，税率,税额
            # ‘价税合计’，none,金额，none,none,none,none,none,none，none，none
            # ‘销售方’，内容，none,none,none,none,‘备注’，备注,none,none,none
            if table and len(table)==4:
                # 购买方
                purchaser = table[0][1].replace(" ", "").replace('　','').replace("\n", "").replace(" ", "")
                match = re.search(r'名称(:|：)(.*)纳税人识别号(:|：)(.*)地址、电话(:|：)(.*)开户行及账号(:|：)(.*)', purchaser)
                invoice.purchaserName = match.group(2)
                invoice.purchaserTaxNumber = match.group(4)
                invoice.purchaserAddress = match.group(6)
                invoice.purchaserBank = match.group(8)
                # 密码区
                invoice.password = table[0][7].replace("\n", "")
                # 货物名
                invoice.serviceType = table[1][0].split("\n")[1].replace(" ", "")
                # 合计金额、税额
                invoice.totalAmount = table[1][8].split("\n")[-1].replace("￥", "").replace(" ", "").replace(",", "")
                invoice.totalAmount = float(invoice.totalAmount)
                # 注意有的发票税额为0是'*',无法直接转成数值
                invoice.totalTax = table[1][10].split("\n")[-1].replace("￥", "").replace(" ", "").replace("*", "").replace('＊','').replace(",", "")
                try:
                    invoice.totalTax = float(invoice.totalTax) if invoice.totalTax else 0
                except:
                    logger.warning('发票税额转换失败：{invoice.totalTax}')
                    invoice.totalTax = 0
                # 税率，一般一张发票中货品税率一致;也可以用(总税额/总金额)计算税率
                invoice.taxRate = table[1][9].split("\n")[-1].replace(" ", "").replace("%", "").replace("*", "0")
                try:
                    invoice.taxRate = float(invoice.taxRate)/100 if invoice.taxRate else 0
                except:
                    logger.warning(f"税率转换失败：{invoice.taxRate}")
                    invoice.taxRate = 0
                # invoice.taxRate = invoice.totalTax / invoice.totalAmount
                # 价税合计,解析或计算
                invoice.total = re.search(r'.+￥(.+)', table[2][2]).group(1).replace(" ", "").replace(",", "")
                invoice.total = float(invoice.total)
                # invoice.total = invoice.totalTax + invoice.totalAmount
                # 销售方
                seller = table[3][1].replace(" ", "").replace('　','').replace("\n", "").replace(" ", "")
                match = re.search(r'名称(:|：)(.*)纳税人识别号(:|：)(.*)地址、电话(:|：)(.*)开户行及账号(:|：)(.*)', seller)
                invoice.sellerName = match.group(2)
                invoice.sellerTaxNumber = match.group(4)
                invoice.sellerAddress = match.group(6)
                invoice.sellerBank = match.group(8)
                # 备注
                invoice.remark = table[3][7].replace("\n", "")
    except Exception as e:
        print(pdf_file, e)
    return invoice

#导出到excel
def export_to_excel(invoices:"list[InvoiceDetailModel]", output_path:str):
    row = len(invoices) if invoices else 0
    if row == 0:
        print("没有可导出的数据")
        return
    try:
        workbook = openpyxl.Workbook()
        sheet=workbook[workbook.sheetnames[0]]
        # 导出开票日期、发票代码、发票号码、校验码、购买方名称和税号、销售方名称和税号、价格、税率、税额、价税合计、备注
        sheet.append(['开票日期','发票代码','发票号码','校验码','购买方名称','购买方税号','销售方名称','销售方税号','价格','税率','税额','价税合计','备注'])
        for i in range(row):
            invoice = invoices[i]
            sheet.append([invoice.date,invoice.code,invoice.number,invoice.checkCode,invoice.purchaserName,invoice.purchaserTaxNumber,invoice.sellerName,invoice.sellerTaxNumber,invoice.totalAmount,invoice.taxRate,invoice.totalTax,invoice.total,invoice.remark])
        workbook.save(output_path)
    except Exception as e:
        print('导出到excel失败', e)

# 合并pdf
def merge_pdf(invoice_paths:"list[str]", output_path:str):
    if len(invoice_paths) == 0:
        print("没有可合并的pdf")
        return
    try:
        merger = PdfFileMerger()
        for invoice_path in invoice_paths:
            merger.append(invoice_path)
        merger.write(output_path)
        merger.close()
    except Exception as e:
        print('合并pdf失败', e)
     
