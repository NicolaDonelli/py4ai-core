import os
import pickle
from io import BytesIO, StringIO
from pathlib import Path
from typing import Type

import pandas as pd
from pydantic import BaseModel

from py4ai.core.data.layer.v1.fs.repository import FileSystemRepository
from py4ai.core.data.layer.v1.fs.serializer import (
    FileSerializer,
    FileSerializerMode,
    IndexedIO,
)


class TabularData(BaseModel):
    name: str = ""
    data: pd.DataFrame

    class Config:
        arbitrary_types_allowed = True

    def update(self, other: "TabularData") -> "TabularData":
        return TabularData(
            name=f"{self.name}/{other.name}" if other.name != self.name else self.name,
            data=pd.concat([self.data, other.data], axis=0),
        )


class CsvSerializer(FileSerializer[str, TabularData]):
    mode = FileSerializerMode.TEXT

    def get_key(self, entity: TabularData) -> str:
        return entity.name

    def to_document_key(self, key: str) -> str:
        return os.path.join(self.path, key + ".csv")

    def to_model(self, document: IndexedIO) -> TabularData:
        data = pd.read_csv(document.buffer, sep=";", dtype=str)
        return TabularData(name=document.name, data=data.set_index(data.columns[0]))

    def to_document(self, entity: TabularData) -> IndexedIO:
        csv_buffer = StringIO()
        entity.data.to_csv(csv_buffer, sep=";")
        csv_buffer.seek(0)
        return IndexedIO(name=self.get_key(entity), buffer=csv_buffer)


class PickleSerializer(CsvSerializer):
    mode = FileSerializerMode.BINARY

    def to_document_key(self, key: str) -> str:
        return os.path.join(self.path, key + ".pkl")

    def to_model(self, document: IndexedIO) -> TabularData:
        return TabularData(name=document.name, data=pd.read_pickle(document.buffer))

    def to_document(self, entity: TabularData) -> IndexedIO:
        buffer = BytesIO()
        buffer.write(pickle.dumps(entity.data, protocol=pickle.HIGHEST_PROTOCOL))
        buffer.seek(0)
        return IndexedIO(name=self.get_key(entity), buffer=buffer)


class LocalDatabase(FileSystemRepository[str, TabularData]):
    def __init__(
        self,
        path: Path,
        serializer: Type[FileSerializer[str, TabularData]] = CsvSerializer,
    ):
        super(LocalDatabase, self).__init__(path, serializer(path))
