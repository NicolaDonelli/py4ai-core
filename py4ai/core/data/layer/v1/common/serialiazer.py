from abc import ABC, abstractmethod
from typing import Generic, TypeVar

KE = TypeVar("KE")
KD = TypeVar("KD")
E = TypeVar("E")
D = TypeVar("D")


class DataSerializer(ABC, Generic[KE, KD, E, D]):
    @abstractmethod
    def get_key(self, entity: E) -> KE:
        ...

    @abstractmethod
    def to_document_key(self, key: KE) -> KD:
        ...

    @abstractmethod
    def to_model(self, document: D) -> E:
        ...

    @abstractmethod
    def to_document(self, entity: E) -> D:
        ...
