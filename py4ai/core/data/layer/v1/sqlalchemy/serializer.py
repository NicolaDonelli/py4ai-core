from abc import ABC
from typing import Dict, Any, Generic

from sqlalchemy import Table

from py4ai.core.data.layer.v1.common.repository import KD, E, KE
from py4ai.core.data.layer.v1.common.serialiazer import DataSerializer


class SqlAlchemySerializer(
    DataSerializer[KE, KD, E, Dict[str, Any]], ABC, Generic[KE, KD, E]
):
    def __init__(self, table: Table):
        self.table = table
