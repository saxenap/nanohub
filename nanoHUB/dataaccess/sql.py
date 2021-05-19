import pymysql
from dataclasses import dataclass
from sshtunnel import SSHTunnelForwarder
import pandas as pd
from pandas.core.frame import DataFrame
from nanoHUB.dataaccess.common import QueryParams, DataframeObject

'''
Connections 
'''


class IConnection:
    def get_connection(self):
        raise NotImplemented


class CachedConnection(IConnection):
    def __init__(self, connection: IConnection):
        self.connection = connection

    def get_connection(self):
        if not hasattr(self, 'cached_connection') or self.cached_connection == None:
            self.cached_connection = self.connection.get_connection()

        return self.cached_connection


@dataclass
class PyMysqlConnection(IConnection):
    db_host: str
    db_username: str
    db_password: str
    db_port: int = 3306

    def get_connection(self) -> pymysql.Connection:
        return pymysql.connect(
            host=self.db_host,
            user=self.db_username,
            passwd=self.db_password,
            port=self.db_port
        )


@dataclass
class TunneledConnection(IConnection):
    ssh_host: str
    ssh_username: str
    ssh_password: str
    remote_bind_address: str
    remote_bind_port: int

    db_host: str
    db_username: str
    db_password: str

    ssh_port: int = 22

    def get_connection(self) -> pymysql.Connection:
        tunnel = SSHTunnelForwarder((
            self.ssh_host, int(self.ssh_port)
        ),
            ssh_password=self.ssh_password,
            ssh_username=self.ssh_username,
            remote_bind_address=(
                self.remote_bind_address, int(self.remote_bind_port)
            )
        )
        tunnel.start()

        pymysql = PyMysqlConnection(
            db_host=self.db_host,
            db_username=self.db_username,
            db_password=self.db_password,
            db_port=tunnel.local_bind_port
        )

        return pymysql.get_connection()


'''
Sql to  DataFrame Mapping
'''


class SqlDataFrameMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams, chunk_size: int, offset: int) -> DataFrame:
        connection = self.connection.get_connection()
        sql = 'SELECT ' + ','.join(
            params.col_names) + ' FROM ' + params.db_name + '.' + params.table_name + ' ' + params.condition + ' ORDER BY ' + params.index_key + ' LIMIT %d OFFSET %d'
        sql = sql % (chunk_size, offset)
        df = pd.read_sql_query(sql, connection, params.index_key)
        return df


'''
Sql Table Information
'''


class ColumnInfoMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams) -> DataFrame:
        sql = 'SELECT COLUMN_NAME , DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "' + params.db_name + '" AND TABLE_NAME = "' + params.table_name + '"'
        return pd.read_sql_query(sql, self.connection.get_connection())


class SqlDataRepository:
    def __init__(self, data_mapper: SqlDataFrameMapper, col_info_mapper: ColumnInfoMapper):
        self.data_mapper = data_mapper
        self.col_info_mapper = col_info_mapper

    def read(self, params: QueryParams, chunk_size: int = 1000000, offset: int = 0):
        col_info_df = self.col_info_mapper.map(params)

        while True:
            df = self.data_mapper.map(params, chunk_size, offset)
            yield DataframeObject(df, col_info_df)

            offset += chunk_size
            if len(df) < chunk_size:
                break


class ITransformer:
    def transform(self, df_object: DataframeObject) -> DataframeObject:
        raise NotImplemented


class DateTimeConvertor(ITransformer):
    def transform(self, df_object: DataframeObject) -> DataframeObject:
        data_df = df_object.get_data()

        col_types_df = df_object.get_col_info()
        df = col_types_df.loc[col_types_df['DATA_TYPE'] == 'datetime']

        for index, row in df.iterrows():
            data_df[row['COLUMN_NAME']] = pandas.to_datetime(data_df[row['COLUMN_NAME']],errors='coerce')

        return DataframeObject(data_df, col_types_df)