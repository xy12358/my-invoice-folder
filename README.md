# my-invoice-folder
一个管理个人发票工具

## 功能
1. 发票自动识别，读取发票信息。（前期只处理PDF电子发票）
2. 批量导出识别的发票信息。
3. 合并多个发票文件到一个文件。
4. 提供可视化界面，支持C/S和B/S两种模式。
5. 添加到windows任务栏。TODO
6. 发票分类。根据报销类型对发票进行分类标注。
7. 发票抬头、税号、发票号等校验，排除错误抬头、避免出现重复发票。
8. 标注已经报销的发票。TODO
9. 自动读取邮箱中的发票附件，并提取发票信息。TODO
10. 支持图片格式增值税发票。基于OCR识别发票。TODO
11. 支持更多其他类型的发票。TODO

## 安装
开发使用的python版本为3.8.6  
安装依赖 `pip install -r requirements.txt`  
运行程序 `python main.py`

## 使用技术
pdfplumber~=0.6.1  
PyPDF4~=1.27.0  
openpyxl~=3.0.7  
fastapi~=0.63.0  
uvicorn~=0.13.3  
loguru~=0.5.3  