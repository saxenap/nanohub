from nanoHUB.dataaccess.common import DataframeObject
import pandas
from pandas.core.frame import DataFrame


class ITransformer:
    def transform(self, data_df: DataFrame, col_info_df: DataFrame) -> DataFrame:
        raise NotImplemented

class DataTransformers(ITransformer):
    def __init__(self, transformers: list = []):
        self.transformers = transformers

    def add_transformer(self, transformer: ITransformer):
        self.transformers.append(transformer)

    def transform(self, data_df: DataFrame, col_info_df: DataFrame) -> DataFrame:
        for transformer in self.transformers:
            data_df = transformer.transform(data_df, col_info_df)

        return data_df


class DateTimeConvertor(ITransformer):
    def transform(self, data_df: DataFrame, col_info_df: DataFrame) -> DataFrame:

        df = col_info_df.loc[col_info_df['DATA_TYPE'] == 'datetime']

        for index, row in df.iterrows():
            data_df[row['COLUMN_NAME']] = pandas.to_datetime(data_df[row['COLUMN_NAME']],errors='coerce')

        return data_df