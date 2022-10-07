from typing import TypeVar

from pydantic import BaseModel

KE = TypeVar("KE")  # entity key
KD = TypeVar("KD")  # data key
E = TypeVar("E", bound=BaseModel)  # entity model
D = TypeVar("D")  # data model
Q = TypeVar("Q")  # search query
A = TypeVar("A")  # aggregate criteria
S = TypeVar("S", bound=BaseModel)  # generic serialized model
U = TypeVar("U")  # for unit of work usage
