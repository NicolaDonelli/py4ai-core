from typing import Optional, Union

from sqlalchemy import and_, or_
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList

from py4ai.core.data.layer.v1.common.criteria import SearchCriteria

SqlAlchemyQuery = Union[BinaryExpression, BooleanClauseList, bool]


class SqlAlchemySearchCriteria(SearchCriteria[SqlAlchemyQuery]):
    def __init__(self, query: Optional[SqlAlchemyQuery] = None):
        self.__query__ = query

    @property
    def query(self) -> BinaryExpression:
        return self.__query__ if self.__query__ is not None else 1 == 1

    def __or__(
        self, other: "SearchCriteria[SqlAlchemyQuery]"
    ) -> "SearchCriteria[SqlAlchemyQuery]":
        return SqlAlchemySearchCriteria(or_(self.query, other.query))

    def __and__(
        self, other: "SearchCriteria[SqlAlchemyQuery]"
    ) -> "SearchCriteria[SqlAlchemyQuery]":
        return SqlAlchemySearchCriteria(and_(self.query, other.query))

    @staticmethod
    def empty() -> "SqlAlchemySearchCriteria":
        return SqlAlchemySearchCriteria()
