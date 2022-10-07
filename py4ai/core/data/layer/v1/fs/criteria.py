import json
import os
from pathlib import Path
from typing import (
    Iterable,
    List,
    Dict,
    Callable,
    Generic,
    Any,
    Tuple,
)

from py4ai.core.data.layer.v1.common.criteria import SearchCriteria
from py4ai.core.data.layer.v1.common.repository import KE, E, SortingDirection
from py4ai.core.utils.dict import union


class FileSystemSearchCriteria(SearchCriteria[List[KE]]):
    def __init__(self, iterable: Iterable[KE]):
        self.__elements__ = [arg for arg in iterable]

    @property
    def query(self) -> List[KE]:
        return list(self.__elements__)

    def __or__(self, other: SearchCriteria) -> "FileSystemSearchCriteria":
        if not isinstance(other, FileSystemSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        return FileSystemSearchCriteria(set(self.query).union(other.query))

    def __and__(self, other: SearchCriteria) -> "FileSystemSearchCriteria":
        if not isinstance(other, FileSystemSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        return FileSystemSearchCriteria(set(self.query).intersection(other.query))


class FileSystemCriteriaFactory(Generic[KE, E]):
    def __init__(self, path: Path, index_file: Path = Path("indices.json")):
        self.path = path
        self.index_file = index_file

    @property
    def index(self) -> Dict[KE, Dict]:
        try:
            with open(os.path.join(self.path, self.index_file), "r") as fid:
                return json.load(fid)
        except FileNotFoundError:
            return {}

    def get_index_fields(self, entity: E) -> Dict[str, Any]:
        return {}

    def update_index(self, key: KE, entity: E):
        data = self.get_index_fields(entity)
        index = self.index
        with open(os.path.join(self.path, self.index_file), "w") as fid:
            json.dump(union(index, {key: data}), fid)

    def filter_path_by_condition(
        self, condition: Callable[[Dict], bool]
    ) -> FileSystemSearchCriteria:
        keys = [key for key, data in self.index.items() if condition(data)]
        return FileSystemSearchCriteria(keys)

    @staticmethod
    def format_name(name: Path, path: Path):
        return os.path.splitext(name.relative_to(path))[0]

    def all(self) -> FileSystemSearchCriteria:
        return FileSystemSearchCriteria(self.index.keys())

    def sort_by(
        self,
        criteria: FileSystemSearchCriteria,
        sorting_option: Tuple[str, SortingDirection],
    ):
        index = self.index
        name, order = sorting_option
        return FileSystemSearchCriteria(
            sorted(
                criteria.query,
                key=lambda key: index[key][name],
                reverse=False if order == SortingDirection.ASC else True,
            )
        )
