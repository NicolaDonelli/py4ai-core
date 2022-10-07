from typing import Any, Dict, Generic, Optional, Union, Sequence

from sqlalchemy import func, select
from sqlalchemy.exc import MultipleResultsFound, NoResultFound
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.sql.elements import BinaryExpression, BooleanClauseList

from py4ai.core.data.layer.v1.common.criteria import SearchCriteria
from py4ai.core.data.layer.v1.common.repository import (
    KD,
    KE,
    AbstractRepository,
    E,
    Paged,
    QueryOptions,
    SortingDirection,
)
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer
from py4ai.core.data.layer.v1.sqlalchemy.criteria import SqlAlchemySearchCriteria
from py4ai.core.data.layer.v1.sqlalchemy.serializer import SqlAlchemySerializer
from py4ai.core.logging.defaults import WithLogging


class SqlAlchemyRepository(
    AbstractRepository[
        KE, KD, E, Dict[str, Any], Union[BinaryExpression, BooleanClauseList]
    ],
    WithLogging,
    Generic[KE, KD, E],
):
    def __init__(
        self, engine: AsyncEngine, serializer: SqlAlchemySerializer[KE, KD, E]
    ):
        self.engine = engine
        self._serializer = serializer
        self.table = serializer.table

    @property
    def serializer(self) -> DataSerializer[KE, KD, E, Dict[str, Any]]:
        return self._serializer

    async def retrieve(self, key: KE) -> Optional[E]:
        try:
            async with self.engine.begin() as connection:
                condition = self.table.c.id == self.serializer.to_document_key(key)
                result = await connection.execute(self.table.select().where(condition))
                raw_entity = result.one()
                return self.serializer.to_model(raw_entity)
        except NoResultFound as e:
            self.logger.info(
                f"Failed to fetch entity with key={str(key)} from repository {str(self)}: {e}"
            )
            return None
        except MultipleResultsFound as e:
            self.logger.info(
                f"Multiple fetch entity with key={str(key)} from repository {str(self)}: {e}"
            )
            return None
        except Exception as e:
            self.logger.error(f"Error occur in retrieving {key}: {e}")
            return None

    async def retrieve_by_criteria(
        self,
        criteria: SearchCriteria[Union[BinaryExpression, BooleanClauseList]],
        options: QueryOptions = QueryOptions(),
    ) -> Paged[E]:
        async with self.engine.begin() as connection:
            number_results = await connection.execute(
                select([func.count()]).select_from(self.table).where(criteria.query)
            )
            number = number_results.first()[0]

            query = self.table.select().where(criteria.query)
            query = (
                query
                if options.page_size < 0
                else query.limit(options.page_size).offset(
                    options.page_start * options.page_size
                )
            )

            for column_name, order in options.sorting_options:
                query = query.order_by(
                    self.table.c[column_name]
                    if order == SortingDirection.ASC
                    else self.table.c[column_name].desc()
                )

            cursor = await connection.execute(query)

            results = cursor.fetchall()  # noqa: E131
            has_more_pages = (
                False
                if options.page_size < 0
                else options.page_size + options.page_start * options.page_size < number
            )

            return Paged(
                number,
                [self.serializer.to_model(doc) for doc in results],
                has_more_pages,
            )

    async def create(self, entity: E) -> E:
        async with self.engine.begin() as connection:
            doc = self.serializer.to_document(entity)
            result = await connection.execute(self.table.insert(doc))
            if result.rowcount > 0:
                return self.serializer.to_model(doc)
            else:
                raise ValueError

    async def list(self, options: QueryOptions = QueryOptions()) -> Paged[E]:
        return await self.retrieve_by_criteria(SqlAlchemySearchCriteria(True), options)

    async def save(self, entities: Sequence[E]) -> Sequence[E]:
        async with self.engine.begin() as connection:
            docs = [self.serializer.to_document(e) for e in entities]
            result = await connection.execute(self.table.insert(), docs)
            if result.rowcount == len(entities):
                return entities
            else:
                raise ValueError

    async def delete(self, key: KE) -> bool:
        async with self.engine.begin() as connection:
            condition = self.table.c.id == self.serializer.to_document_key(key)
            result = await connection.execute(self.table.delete(condition))
            return bool(result.rowcount > 0)

    async def delete_by_criteria(
        self, criteria: SearchCriteria[Union[BinaryExpression, BooleanClauseList]]
    ) -> bool:
        async with self.engine.begin() as connection:
            result = await connection.execute(self.table.delete(criteria.query))
            return bool(result.rowcount > 0)
