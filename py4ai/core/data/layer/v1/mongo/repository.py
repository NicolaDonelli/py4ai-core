from functools import cached_property
from typing import Any, Dict, Generic, Sequence, Optional

from motor.motor_tornado import MotorClientSession, MotorCollection
from pymongo import ReplaceOne
from pymongo.results import BulkWriteResult, DeleteResult, InsertOneResult

from py4ai.core.logging.defaults import WithLogging
from py4ai.core.data.layer.v1.common.criteria import SearchCriteria
from py4ai.core.data.layer.v1.common.repository import (
    AbstractRepository,
    KE,
    E,
    KD,
    QueryOptions,
    Paged,
)
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer
from py4ai.core.data.layer.v1.mongo.criteria import MongoSearchCriteria


class MongoRepository(
    AbstractRepository[KE, KD, E, dict, Dict[str, Any]], Generic[KE, KD, E], WithLogging
):
    """Class implementing a concrete Creed repository."""

    def __init__(
        self,
        collection: MotorCollection,
        serializer: DataSerializer[KE, KD, E, dict],
        session: Optional[MotorClientSession] = None,
    ):
        self.collection = collection
        self._serializer = serializer
        self.session = session

    @cached_property
    def serializer(self) -> DataSerializer[KE, KD, E, dict]:
        return self._serializer

    async def retrieve(self, key: KE) -> Optional[E]:
        try:
            raw_entity = await self.collection.find_one(
                {"_id": self.serializer.to_document_key(key)}
            )
            if raw_entity is None:
                self.logger.info(
                    f"Failed to fetch entity with key={str(key)} from repository {str(self)}"
                )
                return None
            return self.serializer.to_model(raw_entity)
        except Exception as e:
            self.logger.error(f"Error occur in retrieving {key}: {e}")
            return None

    async def retrieve_by_criteria(
        self,
        criteria: SearchCriteria[Dict[str, Any]],
        options: QueryOptions = QueryOptions(),
    ) -> Paged[E]:
        number = await self.collection.count_documents(criteria.query)

        query = self.collection.find(criteria.query)
        cursor = (
            query
            if options.page_size < 0
            else query.limit(options.page_size).skip(
                options.page_start * options.page_size
            )
        )

        if len(options.sorting_options) > 0:
            cursor = cursor.sort(options.sorting_options)

        results = await cursor.to_list(length=None)  # noqa: E131

        has_more_pages = (
            False
            if options.page_size < 0
            else options.page_size + options.page_start * options.page_size < number
        )

        return Paged(
            number, [self.serializer.to_model(doc) for doc in results], has_more_pages
        )

    async def list(self, options: QueryOptions = QueryOptions()) -> Paged[E]:
        return await self.retrieve_by_criteria(MongoSearchCriteria.empty(), options)

    async def create(self, entity: E) -> E:
        doc = self.serializer.to_document(entity)
        result: InsertOneResult = await self.collection.insert_one(
            doc, session=self.session
        )
        doc["_id"] = result.inserted_id
        return self.serializer.to_model(doc)

    async def save(self, entities: Sequence[E]) -> Sequence[E]:
        updates = [
            (
                self.serializer.to_document_key(self.serializer.get_key(entity)),
                self.serializer.to_document(entity),
            )
            for entity in entities
        ]

        _: BulkWriteResult = await self.collection.bulk_write(
            [ReplaceOne({"_id": docId}, doc, upsert=True) for docId, doc in updates],
            ordered=False,
            session=self.session,
        )

        return entities

    async def delete(self, key: KE) -> bool:
        result: DeleteResult = await self.collection.delete_one(
            {"_id": self.serializer.to_document_key(key)}, session=self.session
        )
        return True if (result.deleted_count > 0) else False

    async def delete_by_criteria(
        self, criteria: SearchCriteria[Dict[str, Any]]
    ) -> bool:
        result: DeleteResult = await self.collection.delete_many(
            criteria.query, session=self.session
        )
        return True if (result.deleted_count > 0) else False
