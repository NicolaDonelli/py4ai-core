from abc import ABC, abstractmethod
from typing import Generic

from py4ai.core.data.layer.v1.common import Q


class BaseCriteria(Generic[Q], ABC):
    @property
    @abstractmethod
    def query(self) -> Q:
        ...


class SearchCriteria(BaseCriteria, Generic[Q]):
    @abstractmethod
    def __or__(self, other: "SearchCriteria[Q]") -> "SearchCriteria[Q]":
        ...

    @abstractmethod
    def __and__(self, other: "SearchCriteria[Q]") -> "SearchCriteria[Q]":
        ...
