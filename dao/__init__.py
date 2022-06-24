from model import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.query import Query
from model import Page

class BaseDao(object):

    def __init__(self) -> None:
        self._session = sessionmaker(engine)()
        super().__init__()

    def pagination(self, filter: Query, page: Page = None) -> Query:
        # 没有符合条件的记录，直接返回
        if page is None or page.totalRecords == 0:
            return filter
        else:
            # 当前页码不能小于1 
            if page.currentPage <= 0:
                page.currentPage = 1
            # 计算总页数 
            page.totalPages = int((page.totalRecords + page.pageSize - 1) / page.pageSize)
            # 当前页码不能大于总页数
            if page.currentPage > page.totalPages:
                page.currentPage = page.totalPages

            f = filter.offset((page.currentPage-1)*page.pageSize).limit(page.pageSize)
            return f
