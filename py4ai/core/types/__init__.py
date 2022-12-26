"""Typing utilities."""
import os
from typing import Any, Hashable, TypeVar, Union

from pydantic import BaseModel
from typing_extensions import Protocol

PathLike = Union[str, "os.PathLike[str]"]
T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

# To be used as hashable key
K = TypeVar("K", bound=Hashable)
KE = TypeVar("KE")  # entity key
KD = TypeVar("KD")  # data key
E = TypeVar("E", bound=BaseModel)  # entity model
D = TypeVar("D")  # data model
Q = TypeVar("Q")  # search query
A = TypeVar("A")  # aggregate criteria
S = TypeVar("S", bound=BaseModel)  # generic serialized model
U = TypeVar("U")  # for unit of work usage


class SupportsLessThan(Protocol):
    """Protocol for a class that must support the less than operator."""

    def __lt__(self, other: Any) -> bool:
        """
        Less than operator.

        :param other: other operand
        :return bool: whether self is less than other
        """
        ...
