# -*- encoding: utf-8 -*-
# author: yxin

from loguru import logger
from . import BaseDao
from model import Response
from model.purchaserModel import PurchaserCreateModel,PurchaserModel,PurchaserListModel,PurchaserUpdateModel
from sqlalchemy import func


class PurchaserDao(BaseDao):

    def __init__(self) -> None:
        super().__init__()

    def list(self) -> PurchaserListModel:
        res = PurchaserListModel()
        # 获取购买者列表
        f = self._session.query(PurchaserModel)
        
        res.purchaserList = [PurchaserUpdateModel(**item.__dict__) for item in f.all()]
        return res

    # 删除发票抬头
    def delete(self, id: str) -> Response:
        logger.info(f'删除发票抬头，id={id}')
        try:
            rows = self._session.query(PurchaserModel).filter(PurchaserModel.id==id).delete()
            self._session.commit()
            logger.info(f'删除发票抬头成功，删除了{rows}条记录')
            return Response(code=200, message='ok')
        except Exception as e:
            logger.error(e)
            self._session.rollback()
            return Response(code=500, message='delete failed')

    # 新增发票抬头
    def add(self, purchaserCreateModel: PurchaserCreateModel) -> Response:
        logger.info(f'添加发票抬头，抬头信息={purchaserCreateModel}')
        try:
            purchaser = PurchaserModel(**purchaserCreateModel.dict())
            self._session.add(purchaser)
            self._session.commit()
            return Response(code=200, message='ok')
        except Exception as e:
            logger.error(e)
            self._session.rollback()
            return Response(code=500, message='add failed')

    
    # 更新发票抬头
    def update(self, purchaserUpdateModel: PurchaserUpdateModel) -> Response:
        logger.info(f'更新发票抬头，抬头信息={purchaserUpdateModel}')
        try:
            purchaser = self._session.query(PurchaserModel).filter(PurchaserModel.id==purchaserUpdateModel.id).first()
            purchaser.name = purchaserUpdateModel.name
            purchaser.address = purchaserUpdateModel.address
            purchaser.phone = purchaserUpdateModel.phone
            purchaser.bankName = purchaserUpdateModel.bankName
            purchaser.bankAccount = purchaserUpdateModel.bankAccount
            purchaser.taxNumber = purchaserUpdateModel.taxNumber
            self._session.commit()
            return Response(code=200, message='ok')
        except Exception as e:
            logger.error(e)
            self._session.rollback()
            return Response(code=500, message='update failed')