from abc import ABC
from enum import Enum
from io import IOBase
from pathlib import Path
from typing import Generic

from pydantic import BaseModel

from py4ai.core.data.layer.v1.common.repository import KE, E
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer


class IndexedIO(BaseModel, Generic[KE]):
    name: KE
    buffer: IOBase

    class Config:
        arbitrary_types_allowed = True


class FileSerializerMode(str, Enum):
    TEXT = ""
    BINARY = "b"


class FileSerializer(Generic[KE, E], DataSerializer[KE, str, E, IndexedIO], ABC):
    mode: FileSerializerMode = FileSerializerMode.TEXT

    def __init__(self, path: Path, encoding: str = "utf-8"):
        self.path = path
        self.encoding = encoding if self.mode is FileSerializerMode.TEXT else None

    @classmethod
    def set_path(cls, path: Path) -> "FileSerializer":
        return cls(path)
