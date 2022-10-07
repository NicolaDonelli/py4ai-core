from abc import ABC, abstractmethod
from enum import IntEnum
from typing import Generic, List, Optional, Tuple, Sequence

from py4ai.core.data.layer.v1.common import KD, KE, D, E, Q
from py4ai.core.data.layer.v1.common.criteria import SearchCriteria
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer


class Paged(Generic[E]):
    items: List[E]
    size: int
    more_pages: bool

    def __init__(self, size: int, items: List[E], more_pages: bool):
        self.items = items
        self.size = size
        self.more_pages = more_pages


class SortingDirection(IntEnum):
    DES = -1
    ASC = 1


class QueryOptions:
    def __init__(
        self,
        page_start: int = 0,
        page_size: int = -1,
        sorting_options: List[Tuple[str, SortingDirection]] = [],
    ):
        """
        Implement the options to be used in a query call in the repository abstraction.

        Parameters:
                page_start (int): set the current page
                page_size (int): set the size of paging (default value is -1 - all result are returned in one page)
                sorting_options: a list of options for ordering results
        """
        self.page_start: int = page_start
        self.page_size: int = page_size
        self.sorting_options: List[Tuple[str, SortingDirection]] = sorting_options

    def copy(
        self,
        page_start: Optional[int] = 0,
        page_size: Optional[int] = -1,
        sorting_options: Optional[List[Tuple[str, SortingDirection]]] = None,
    ) -> "QueryOptions":
        return QueryOptions(
            page_start if page_start else self.page_start,
            page_size if page_size else self.page_size,
            sorting_options if sorting_options else self.sorting_options,
        )


class AbstractRepository(Generic[KE, KD, E, D, Q], ABC):
    @property
    @abstractmethod
    def serializer(self) -> DataSerializer[KE, KD, E, D]:
        ...

    @abstractmethod
    async def create(self, entity: E) -> E:
        ...

    async def retrieve(self, key: KE) -> Optional[E]:
        ...

    @abstractmethod
    async def retrieve_by_criteria(
        self, criteria: SearchCriteria[Q], options: QueryOptions = QueryOptions()
    ) -> Paged[E]:
        ...

    @abstractmethod
    async def list(self, options: QueryOptions = QueryOptions()) -> Paged[E]:
        ...

    @abstractmethod
    async def save(self, entities: Sequence[E]) -> Sequence[E]:
        ...

    @abstractmethod
    async def delete(self, key: KE) -> bool:
        ...

    @abstractmethod
    async def delete_by_criteria(self, criteria: SearchCriteria[Q]) -> bool:
        ...
