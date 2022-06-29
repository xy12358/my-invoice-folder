# -*- encoding: utf-8 -*-
# author: yxin
import uvicorn
from multiprocessing import freeze_support
from multiprocessing import Process
import time,sys
import requests
import webbrowser

from config import appConfig
from log import logger

# 启动WebAPI
def runUvicorn():
    uvicorn.run("webapi:app", host=appConfig.uvicorn["host"], port=appConfig.uvicorn["port"], reload=False, log_config='config/uvicornLog.json', access_log=True, workers=1)

# 打开主页
def openBrowser(url: str) -> bool:
    webbrowser.open(url)
    return True

if __name__ == "__main__":
    freeze_support()  
    
    logger.info("application is starting...")

    # 启动web服务
    webapiProcess = Process(target=runUvicorn, name="webapi_process", daemon=True)
    webapiProcess.start()

    # 启动系统默认浏览器打开界面
    waitWebServerTime = appConfig.config["waitWebServerTime"]
    openBrowserSuccess = False
    while waitWebServerTime > 0:
        time.sleep(1)
        try:
            # 判断web服务是否已启动
            indexUrl = f'http://{appConfig.uvicorn["host"]}:{appConfig.uvicorn["port"]}/'
            response = requests.get(indexUrl, timeout=1)
            if response.status_code == 200:
                # 打开主页
                openBrowserSuccess = openBrowser(indexUrl)
                break
        except Exception as e:
            pass
        waitWebServerTime -= 1

    if openBrowserSuccess:
        logger.info("open web browser success")
    else:
        logger.info("open web browser failed, close application")
        sys.exit(1)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("user interrupt, close application")

    sys.exit(0)
    