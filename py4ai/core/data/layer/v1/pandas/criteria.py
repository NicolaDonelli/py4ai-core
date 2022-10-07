from typing import Callable

import pandas as pd

from py4ai.core.data.layer.v1.common.criteria import SearchCriteria

PandasFilter = Callable[[pd.DataFrame], pd.Series]


class PandasSearchCriteria(SearchCriteria[PandasFilter]):
    def __init__(self, condition: PandasFilter):
        self.condition = condition

    @property
    def query(self) -> PandasFilter:
        return self.condition

    def __or__(self, other: SearchCriteria) -> "PandasSearchCriteria":
        if not isinstance(other, PandasSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        return PandasSearchCriteria(lambda df: self.query(df) | other.query(df))

    def __and__(self, other: SearchCriteria) -> "PandasSearchCriteria":
        if not isinstance(other, PandasSearchCriteria):
            raise ValueError(
                f"Inconsistent type for criteria combination: {type(other)} and {type(self)}"
            )
        return PandasSearchCriteria(lambda df: self.query(df) & other.query(df))

    @staticmethod
    def empty() -> "PandasSearchCriteria":
        return PandasSearchCriteria(lambda df: df.apply(lambda x: True, axis=1))
