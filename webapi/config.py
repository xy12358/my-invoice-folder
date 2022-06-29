# -*- encoding: utf-8 -*-
# author: yxin

from fastapi import APIRouter, Path
from model import Response
from model.configModel import ConfigDetailModel
from dao.configDao import ConfigDao

router = APIRouter()
configDao = ConfigDao()


# 获取费用类型
@router.get("/feetypes", response_model=ConfigDetailModel)
async def feeTypes():
    return configDao.getByKey('feeTypes')


# 更新购买方
@router.put("/feetypes/{value}", response_model=Response)
async def updateFeeTypes(value: str = Path(..., title='feeTypes 未分类,交通,住宿,餐饮,通讯,办公,快递,其他', regex="^\S*$")):
    return configDao.update(ConfigDetailModel(key='feeTypes', value=value))
    


