from __future__ import annotations
from typing import TYPE_CHECKING, ClassVar
import pandas as pd
from pandasai.dataframe.base import DataFrame

if TYPE_CHECKING:
    from pandasai.data_loader.loader import DatasetLoader


class VirtualDataFrame(DataFrame):
    _metadata: ClassVar[list] = [
        "_loader",
        "head",
        "_head",
        "name",
        "description",
        "schema",
        "config",
        "_agent",
        "_column_hash",
    ]

    def __init__(self, *args, **kwargs):
        self._loader: DatasetLoader = kwargs.pop("data_loader", None)
        if not self._loader:
            raise Exception("Data loader is required for virtualization!")
        self._head = None
        super().__init__(self.get_head(), *args, **kwargs)

    def head(self):
        if self._head is None:
            self._head = self._loader.load_head()

        return self._head

    @property
    def rows_count(self) -> int:
        return self._loader.get_row_count()

    def execute_sql_query(self, query: str) -> pd.DataFrame:
        return self._loader.execute_query(query)
