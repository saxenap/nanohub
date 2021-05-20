import pymysql
from dataclasses import dataclass
from sshtunnel import SSHTunnelForwarder
import pandas 
from pandas.core.frame import DataFrame
from nanoHUB.dataaccess.common import QueryParams, DataframeObject
from nanoHUB.dataaccess.cache import CachedDataLoader
from nanoHUB.dataaccess.transformers import ITransformer

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
    def __init__(self, connection: IConnection, chunk_size: int = 1000000):
        self.connection = connection
        self.chunk_size = chunk_size

    def map(self, params: QueryParams) -> DataFrame:
        connection = self.connection.get_connection()
        offset = 0
        while True:
            sql = 'SELECT ' + ','.join(
                params.col_names) + ' FROM ' + params.db_name + '.' + params.table_name + ' ' + params.condition + ' ORDER BY ' + params.index_key + ' LIMIT %d OFFSET %d'
            sql = sql % (self.chunk_size, offset)
            df = pandas.read_sql_query(sql, connection, params.index_key)
            yield df

            offset += self.chunk_size
            if len(df) < self.chunk_size:
                break

    def get_table_info(self, params: QueryParams) -> DataFrame:
        sql = 'SELECT COLUMN_NAME , DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "' + params.db_name + '" AND TABLE_NAME = "' + params.table_name + '"'

        if params.col_names[0] != '*':
            sql = sql + ' AND (COLUMN_NAME = "' + '" OR COLUMN_NAME = "'.join(params.col_names) + '")'

        return pandas.read_sql_query(sql, self.connection.get_connection())

'''
ETL
'''

class ETL:
    def __init__(
        self, data_mapper: SqlDataFrameMapper, transformer: ITransformer, loader: CachedDataLoader
    ):
        self.data_mapper = data_mapper
        self.transformer = transformer
        self.loader = loader

    def __call__(self, params: QueryParams) -> DataFrame:

        if not self.loader.exists(params):
            table_info = self.data_mapper.get_table_info(params)
            for partial_df in self.data_mapper.map(params):
                partial_df = self.transformer.transform(partial_df, table_info)
                self.loader.save(partial_df, params)

        return self.loader.get(params)


