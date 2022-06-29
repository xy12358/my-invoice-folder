# -*- encoding: utf-8 -*-
# author: yxin

from loguru import logger
from . import BaseDao
from model import Response
from model.configModel import ConfigModel,ConfigDetailModel
from datetime import datetime


class ConfigDao(BaseDao):

    def __init__(self) -> None:
        super().__init__()

    # 获取配置项
    def getByKey(self, key: str) -> ConfigDetailModel:
        res = self._session.query(ConfigModel).filter_by(key=key).first()
        return ConfigDetailModel() if not res else ConfigDetailModel(**res.__dict__)

    # 添加配置项
    def add(self, configModel: ConfigDetailModel) -> Response:
        try:
            self._session.add(ConfigModel(**configModel.dict()))
            self._session.commit()
            return Response()
        except Exception as e:
            logger.error(e)
            return Response(code=500, message='添加配置项失败')
    
    # 更新配置项
    def update(self, configModel: ConfigDetailModel) -> Response:
        try:
            self._session.query(ConfigModel).filter_by(key=configModel.key).update({ConfigModel.value: configModel.value, ConfigModel.timestamp: datetime.now()})
            self._session.commit()
            return Response()
        except Exception as e:
            logger.error(e)
            return Response(code=500, message='更新配置项失败')