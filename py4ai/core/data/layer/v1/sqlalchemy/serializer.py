"""Module for implementing the Serializer to be used in SQL persistence layers."""

from abc import ABC
from typing import Any, Dict, Generic

from sqlalchemy import Table

from py4ai.core.data.layer.v1.common.repository import KD, KE, E
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer


class SqlAlchemySerializer(
    DataSerializer[KE, KD, E, Dict[str, Any]], ABC, Generic[KE, KD, E]
):
    """Serializer to be used in SQL persistence layers."""

    def __init__(self, table: Table):
        """Instantiate the serializer based on the input table.

        :param table: SQL table to be used in the persistence layer.
        """
        self.table = table
