from random import randint
from typing import Callable, Optional
from fastapi import FastAPI,Request
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html,get_swagger_ui_oauth2_redirect_html
from fastapi.responses import RedirectResponse
from loguru import logger
from datetime import datetime
from contextvars import ContextVar

# 用于日志记录当前请求ID
transaction_id: ContextVar[Optional[str]] = ContextVar('transaction_id', default='')

def transaction_id_filter(record):
    record['extra']['tid'] = transaction_id.get()
    return record

# 此处设置tid
logger.configure(patcher=transaction_id_filter)

app = FastAPI(title='My Invoice Folder', docs_url=None, redoc_url=None)

# 生成请求ID
@app.middleware("http")
async def create_transaction_id(request: Request, call_next: Callable):
    # tid格式为时间戳+4位随机数
    transaction_id.set(f"{datetime.now().strftime('%Y%m%d%H%M%S%f')[:-3]}{randint(1000, 9999)}")
    response = await call_next(request)
    return response

# 静态资源
app.mount("/ui", StaticFiles(directory="ui"), name="ui")

# 首页跳转到我的发票夹页面
@app.get("/", include_in_schema=False)
def read_root():
    logger.info("access index page")
    return RedirectResponse("/ui/index.html")

# swagger ui使用本地资源
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title="LUGGAGE ENGINE",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/ui/static/swagger-ui-bundle.js",
        swagger_css_url="/ui/static/swagger-ui.css",
        swagger_favicon_url="/ui/static/favicon.png",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()