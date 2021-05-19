import pymysql
from dataclasses import dataclass
from sshtunnel import SSHTunnelForwarder
import pandas as pd
from pandas.core.frame import DataFrame

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
Query Params
'''


@dataclass
class QueryParams:
    db_name: str
    table_name: str
    col_names: []
    index_key: str
    condition: str = ''


'''
Sql to  DataFrame Mapping
'''


class DataFrameMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams, chunk_size: int, offset: int) -> DataFrame:
        connection = self.connection.get_connection()
        sql = 'SELECT ' + ','.join(
            params.col_names) + ' FROM ' + params.db_name + '.' + params.table_name + ' ' + params.condition + ' LIMIT %d OFFSET %d'
        sql = sql % (chunk_size, offset)
        df = pd.read_sql_query(sql, connection)
        # df = df.set_index(params.index_key)
        return df


'''
Sql Table Information
'''


class ColumnInfoDataFrameMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams) -> DataFrame:
        sql = 'SELECT COLUMN_NAME , DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = ' + params.db_name + ' AND TABLE_NAME = ' + params.table_name
        return pd.read_sql_query(sql, self.connection.get_connection())
