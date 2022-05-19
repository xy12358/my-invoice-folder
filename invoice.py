import pdfplumber
from PyPDF4 import PdfFileMerger
import openpyxl
import re,time,os

class Invoice:
    def __init__(self):
        # 发票类型、发票号码、开票日期、机器编号、发票代码、校验码
        self.type=self.number=self.date=self.machine_number=self.code=self.check_code = ''
        # 收款人、复核、开票人
        self.payee=self.reviewer=self.drawer = ''
        # 购买方名称、纳税人识别号、地址电话、开户行及账号
        self.purchaser_name=self.purchaser_tax_number=self.purchaser_address=self.purchaser_bank = ''
        # 密码
        self.password = ''
        # 合计金额、合计税额、税率、价税合计
        self.total_amount=self.total_tax=self.tax_rate=self.total = ''
        # 销售方名称、纳税人识别号、地址电话、开户行及账号
        self.seller_name=self.seller_tax_number=self.seller_address=self.seller_bank = ''
        # 备注
        self.remark = ''

    # 解析PDF格式电子发票
    @staticmethod
    def read_invoice(pdf_file: str) -> "Invoice":
        invoice = Invoice()
        try:
            with pdfplumber.open(pdf_file) as pdf:
                # 读取第一页
                first_page = pdf.pages[0]
                # 读取文本
                text = first_page.extract_text().replace(" ", "")
                # print(text)
                if '专用发票' in text:
                    invoice.type = '专票'
                elif '普通发票' in text:
                    invoice.type = '普票'
                else:
                   raise Exception('未知发票类型或非发票文件')

                # 提取发票表格上方内容
                invoice.number = re.search(r'发票号码(:|：)(\d+)', text).group(2)
                invoice.date = re.search(r'开票日期(:|：)(.*)', text).group(2)
                invoice.machine_number = re.search(r'机器编号(:|：)(\d+)', text).group(2)
                invoice.code = re.search(r'发票代码(:|：)(\d+)', text).group(2)
                invoice.check_code = re.search(r'校验码(:|：)(\d+)', text).group(2)
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
                    purchaser = table[0][1].replace(" ", "")
                    purchaser_name = re.search(r'名称(:|：)(.+)', purchaser)
                    invoice.purchaser_name = purchaser_name.group(2) if purchaser_name else ''
                    purchaser_tax_number = re.search(r'纳税人识别号(:|：)(.+)', purchaser)
                    invoice.purchaser_tax_number = purchaser_tax_number.group(2) if purchaser_tax_number else ''
                    purchaser_address = re.search(r'地址、电话(:|：)(.+)', purchaser)
                    invoice.purchaser_address = purchaser_address.group(2) if purchaser_address else ''
                    purchaser_bank = re.search(r'开户行及账号(:|：)(.+)', purchaser)
                    invoice.purchaser_bank = purchaser_bank.group(2) if purchaser_bank else ''
                    # 密码区
                    invoice.password = table[0][7].replace("\n", "")
                    # 合计金额、税额
                    invoice.total_amount = table[1][8].split("\n")[-1].replace("￥", "").replace(" ", "").replace(",", "")
                    invoice.total_amount = float(invoice.total_amount)
                    # 注意有的发票税额为0是'*',无法直接转成数值
                    invoice.total_tax = table[1][10].split("\n")[-1].replace("￥", "").replace(" ", "").replace("*", "0").replace(",", "")
                    invoice.total_tax = float(invoice.total_tax) if invoice.total_tax else 0
                    # 税率，一般一张发票中货品税率一致;也可以用(总税额/总金额)计算税率
                    invoice.tax_rate = table[1][9].split("\n")[-1].replace(" ", "").replace("%", "").replace("*", "0")
                    invoice.tax_rate = float(invoice.tax_rate)/100 if invoice.tax_rate else 0
                    # invoice.tax_rate = invoice.total_tax / invoice.total_amount
                    # 价税合计,解析或计算
                    invoice.total = re.search(r'.+￥(.+)', table[2][2]).group(1).replace(" ", "").replace(",", "")
                    invoice.total = float(invoice.total)
                    # invoice.total = invoice.total_tax + invoice.total_amount
                    # 销售方
                    seller = table[3][1].replace(" ", "")
                    invoice.seller_name = re.search(r'名称(:|：)(.+)', seller).group(2)
                    invoice.seller_tax_number = re.search(r'纳税人识别号(:|：)(.+)', seller).group(2)
                    seller_address = re.search(r'地址、电话(:|：)(.+)', seller)
                    invoice.seller_address = seller_address.group(2) if seller_address else ''
                    seller_bank = re.search(r'开户行及账号(:|：)(.+)', seller)
                    invoice.seller_bank = seller_bank.group(2) if seller_bank else ''
                    # 备注
                    invoice.remark = table[3][7].replace("\n", "")
        except Exception as e:
            print(pdf_file, e)
        return invoice

    #导出到excel
    @staticmethod
    def export_to_excel(invoices:"list[Invoice]", output_path:str):
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
                sheet.append([invoice.date,invoice.code,invoice.number,invoice.check_code,invoice.purchaser_name,invoice.purchaser_tax_number,invoice.seller_name,invoice.seller_tax_number,invoice.total_amount,invoice.tax_rate,invoice.total_tax,invoice.total,invoice.remark])
            workbook.save(output_path)
        except Exception as e:
            print('导出到excel失败', e)

    # 合并pdf
    @staticmethod
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
         

if __name__ == '__main__':
    # 发票所在文件夹，使用绝对路径
    path = r'E:\playground\python_tools\pdf'
    # 输出文件路径
    output_path = os.path.join(path, 'output')
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 发票内容列表
    invoices = []
    # 发票文件路径列表
    invoice_paths = []
    #列出目录的下所有文件
    lists = os.listdir(path)
    for item in lists:
        if item.endswith('.pdf'):
            item = os.path.join(path, item)
            invoice = Invoice.read_invoice(item)
            # 仅保存解析成功的pdf
            if invoice and invoice.type:
                invoices.append(invoice)
                invoice_paths.append(item)
    # 导出发票内容到excel
    Invoice.export_to_excel(invoices, f'{output_path}/invoice_{time.strftime("%Y%m%d_%H%M%S", time.localtime())}.xlsx')
    # 合并发票到一个pdf
    Invoice.merge_pdf(invoice_paths, f'{output_path}/merged_invoice_{time.strftime("%Y%m%d_%H%M%S", time.localtime())}.pdf')