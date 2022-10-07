import asyncio
import os
from pathlib import Path
from typing import Generic, List, Optional, cast, Sequence

from py4ai.core.data.layer.v1.common.repository import (
    AbstractRepository,
    Paged,
    QueryOptions,
    SearchCriteria,
)
from py4ai.core.data.layer.v1.fs import create_dir_if_not_exists
from py4ai.core.data.layer.v1.fs.criteria import (
    FileSystemCriteriaFactory,
    FileSystemSearchCriteria,
)
from py4ai.core.data.layer.v1.fs.serializer import KE, E, FileSerializer, IndexedIO


class FileSystemRepository(
    AbstractRepository[KE, str, E, IndexedIO, List[KE]], Generic[KE, E]
):
    criteria: FileSystemCriteriaFactory

    def __init__(self, path: Path, serializer: FileSerializer[KE, E]):
        self.path = create_dir_if_not_exists(path)
        self._serializer = serializer.set_path(path)

    @property
    def serializer(self) -> FileSerializer[KE, E]:
        return self._serializer

    async def create(self, entity: E) -> E:
        ibuffer = self.serializer.to_document(entity)
        path_to_file = self.serializer.to_document_key(ibuffer.name)
        _ = create_dir_if_not_exists(os.path.dirname(path_to_file))
        with open(
            path_to_file, "w" + self.serializer.mode, encoding=self.serializer.encoding
        ) as fid:
            fid.write(ibuffer.buffer.read())
        self.criteria.update_index(self.serializer.get_key(entity), entity)
        return entity

    async def retrieve(self, key: KE) -> Optional[E]:
        file_name = self.serializer.to_document_key(key)
        if os.path.exists(file_name):
            with open(
                file_name, "r" + self.serializer.mode, encoding=self.serializer.encoding
            ) as fid:
                x: E = self.serializer.to_model(IndexedIO(name=key, buffer=fid))
                return x
        else:
            return None

    async def retrieve_by_criteria(
        self, criteria: SearchCriteria[List[KE]], options: QueryOptions = QueryOptions()
    ) -> Paged[E]:
        if len(options.sorting_options) > 0:
            if len(options.sorting_options) > 1:
                raise ValueError(
                    "Multiple sorting options are not allowed for FileSystemRepository"
                )
            criteria = self.criteria.sort_by(
                cast(FileSystemSearchCriteria, criteria), options.sorting_options[0]
            )

        query = criteria.query

        selection = (
            query
            if options.page_size < 0
            else query[
                options.page_start : options.page_start + options.page_size
            ]  # noqa: ignore
        )
        all_elements = await asyncio.gather(*[self.retrieve(key) for key in selection])
        elements = [element for element in all_elements if element is not None]
        size = len(elements)
        return Paged(size, elements, options.page_start + size < len(selection))

    async def update(self, entity: E) -> Optional[E]:
        return await self.create(entity)

    async def save(self, entities: Sequence[E]) -> Sequence[E]:
        elements: List[Optional[E]] = await asyncio.gather(
            *[self.update(entity) for entity in entities]
        )
        return [element for element in elements if element is not None]

    async def delete(self, key: KE) -> bool:
        try:
            os.remove(self.serializer.to_document_key(key))
            return True
        except Exception:
            return False

    async def delete_by_criteria(self, criteria: SearchCriteria[List[KE]]) -> bool:
        return all(await asyncio.gather(*[self.delete(key) for key in criteria.query]))

    async def list(self, options: QueryOptions = QueryOptions()) -> Paged[E]:
        return await self.retrieve_by_criteria(self.criteria.all(), options)
