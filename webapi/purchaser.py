from fastapi import APIRouter, Body, Path
from model import Response
from model.purchaserModel import PurchaserUpdateModel,PurchaserCreateModel,PurchaserListModel
from dao.purchaserDao import PurchaserDao

router = APIRouter()
purchaserDao = PurchaserDao()


# 查询购买方列表
@router.post("/list", response_model=PurchaserListModel)
async def list():
    return purchaserDao.list()

# 新增购买方
@router.post("", response_model=Response)
async def add(purchaserCreateModel: PurchaserCreateModel = Body(...)):
    purchaserCreateModel.taxNumber = purchaserCreateModel.taxNumber.upper()
    return purchaserDao.add(purchaserCreateModel)

# 删除购买方
@router.delete("/{id}", response_model=Response)
async def delete(id: str = Path(..., title='ids of purchaser', regex="^\w{25}$")):
    return purchaserDao.delete(id)

# 更新购买方
@router.put("/{id}", response_model=Response)
async def update(id: str = Path(..., title='id of purchaser', regex="^\w{25}$"), purchaserUpdateModel: PurchaserUpdateModel = Body(...)):
    purchaserUpdateModel.id = id
    return purchaserDao.update(purchaserUpdateModel)
    


