from dataclasses import dataclass, field
from pandas.core.frame import DataFrame


@dataclass
class QueryParams:
    db_name: str
    table_name: str
    col_names: [] = field(default_factory=lambda: ['*'])
    index_key: str = ''
    condition: str = ''


class DataframeObject:
    def __init__(self, data: DataFrame, col_info: DataFrame):
        self.data = data
        self.col_info = col_info

    def get_data(self) -> DataFrame:
        return self.data

    def get_col_info(self) -> DataFrame:
        return self.col_info


