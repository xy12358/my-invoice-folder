# -*- encoding: utf-8 -*-
# author: yxin
from loguru import logger
import sys
from config import appConfig

logger.remove()
logger.configure(extra={"tid":"", "data":{}})
logger.add(sys.stderr,  enqueue=True, format=appConfig.loguru["format"], level=appConfig.loguru["level"])
logger.add(appConfig.loguru["file"], enqueue=True, format=appConfig.loguru["format"], level=appConfig.loguru["level"], rotation=appConfig.loguru["rotation"], retention=appConfig.loguru["retention"])