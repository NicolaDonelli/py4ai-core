from typing import Any, Dict, Optional

from py4ai.core.data.layer.v1.common.criteria import SearchCriteria


class MongoSearchCriteria(SearchCriteria[Dict[str, Any]]):
    def __init__(self, query: Optional[Dict[str, Any]] = None):
        self.__query__ = query

    @property
    def query(self) -> Dict[str, Any]:
        return self.__query__ if self.__query__ is not None else dict()

    def __or__(self, other: SearchCriteria) -> "MongoSearchCriteria":
        if not isinstance(other, MongoSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        queries = [self.query, other.query]
        return MongoSearchCriteria({"$or": queries})

    def __and__(self, other: SearchCriteria) -> "MongoSearchCriteria":
        if not isinstance(other, MongoSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        queries = [self.query, other.query]
        return MongoSearchCriteria({"$and": queries})

    @staticmethod
    def empty() -> "MongoSearchCriteria":
        return MongoSearchCriteria()
