from loguru import logger
from . import BaseDao
from model import Response
from model.invoiceModel import InvoiceModel,InvoiceCreateModel,InvoiceUpdateModel,InvoiceQueryModel,InvoiceQueryParams,InvoiceList,InvoiceDetailModel
from sqlalchemy import func
from sqlalchemy.orm.query import Query


class InvoiceDao(BaseDao):

    def __init__(self) -> None:
        super().__init__()

    def buildQuery(self, query: Query, invoiceQueryModel: InvoiceQueryModel) -> Query:
        if invoiceQueryModel.dateType == 0:
            query = query.filter(InvoiceModel.date >= invoiceQueryModel.startDate, InvoiceModel.date <= invoiceQueryModel.endDate+'-31')
        elif invoiceQueryModel.dateType == 1:
            query = query.filter(func.strftime('%Y-%m', InvoiceModel.timestamp) >= invoiceQueryModel.startDate, func.strftime('%Y-%m-%d', InvoiceModel.timestamp) <= invoiceQueryModel.endDate+'-31')
        if invoiceQueryModel.purchaserName:
            query = query.filter(InvoiceModel.purchaserName == invoiceQueryModel.purchaserName)
        if invoiceQueryModel.used:
            query = query.filter(InvoiceModel.used == invoiceQueryModel.used)
        if invoiceQueryModel.feeType:
            query = query.filter(InvoiceModel.feeType.in_(invoiceQueryModel.feeType))
        return query

    def list(self, invoiceQueryParams: InvoiceQueryParams = None) -> InvoiceList:
        res = InvoiceList()
        # 获取发票数量
        f = self._session.query(func.count(InvoiceModel.id))

        if invoiceQueryParams and invoiceQueryParams.query:
            query = invoiceQueryParams.query
            res.query = query
            f = self.buildQuery(f, query)

        count = f.scalar()

        # 获取发票列表
        f = self._session.query(InvoiceModel)
        if query:
            f = self.buildQuery(f, query)
        if invoiceQueryParams and invoiceQueryParams.page:
            page = invoiceQueryParams.page
            page.totalRecords = count
            # 分页
            f = self.pagination(f, page)
            res.page = invoiceQueryParams.page
        
        res.invoiceList = [InvoiceDetailModel(**item.to_dict()) for item in f.all()]
        return res

    def queryById(self, id: str) -> InvoiceDetailModel:
        # 获取发票详情
        res = self._session.query(InvoiceModel).filter_by(id=id).first()
        return InvoiceDetailModel(**res.to_dict()) if res else None

    def queryByIds(self, id: str) -> InvoiceList:
        # 获取发票详情列表
        ids = id.split(',')
        res = InvoiceList()
        try:
            f = self._session.query(InvoiceModel).filter(InvoiceModel.id.in_(ids))
            res.invoiceList = [InvoiceDetailModel(**item.to_dict()) for item in f.all()]
        except Exception as e:
            logger.error(e)

        return res

    # 删除发票
    def delete(self, id: str) -> Response:
        logger.info(f'删除发票，id={id}')
        ids = id.split(',')
        try:
            rows = self._session.query(InvoiceModel).filter(InvoiceModel.id.in_(ids)).delete(synchronize_session=False)
            self._session.commit()
            logger.info(f'删除发票成功，删除了{rows}条记录')
            return Response(code=200, message='ok')
        except Exception as e:
            self._session.rollback()
            return Response(code=500, message='delete failed')


    # 更新发票状态
    def updateStatus(self, status: str, id: str) -> Response:
        logger.info(f'更新发票状态，id={id},status={status}')
        ids = id.split(',')
        try:
            rows = self._session.query(InvoiceModel).filter(InvoiceModel.id.in_(ids)).update({InvoiceModel.used: status})
            self._session.commit()
            logger.info(f'更新发票状态成功，更新了{rows}条记录')
            return Response(code=200, message='ok')
        except Exception as e:
            self._session.rollback()
            return Response(code=500, message='update failed')


    # 更新发票费用类型
    def updateFeeType(self, feeType: str, id: str) -> Response:
        logger.info(f'更新发票费用类型，id={id},feeType={feeType}')
        ids = id.split(',')
        try:
            rows = self._session.query(InvoiceModel).filter(InvoiceModel.id.in_(ids)).update({InvoiceModel.feeType: feeType})
            self._session.commit()
            logger.info(f'更新发票费用类型成功，更新了{rows}条记录')
            return Response(code=200, message='ok')
        except Exception as e:
            self._session.rollback()
            return Response(code=500, message='update failed')

    def add(self, invoiceCreateModel: InvoiceCreateModel, filePath: str = '', addType: str = '0') -> Response:
        logger.info(f'添加发票，发票信息={invoiceCreateModel}')
        try:
            invoice = InvoiceModel(**invoiceCreateModel.dict())
            invoice.filePath = filePath
            invoice.addType = addType
            self._session.add(invoice)
            self._session.commit()
            return Response(code=200, message='ok')
        except Exception as e:
            self._session.rollback()
            return Response(code=500, message='add failed')

    def update(self, invoiceUpdateModel: InvoiceUpdateModel) -> Response:
        logger.info(f'更新发票，发票信息={invoiceUpdateModel}')
        try:
            invoice = invoiceUpdateModel.dict()
            invoice.pop('id')
            self._session.query(InvoiceModel).filter_by(id=invoiceUpdateModel.id).update(invoice)
            self._session.commit()
            return Response(code=200, message='ok')
        except Exception as e:
            self._session.rollback()
            return Response(code=500, message='update failed')
