import os
from pathlib import Path
from sshtunnel import SSHTunnelForwarder
import pymysql
import pandas as pd
from pandas.core.frame import DataFrame
from dotenv import load_dotenv
from dataclasses import dataclass

load_dotenv()



class IConnection:
    def get_connection(self):
        raise NotImplemented


@dataclass
class PyMysql(IConnection):

    db_host: str
    db_port: int
    db_username: str
    db_password: str

    def get_connection(self) -> pymysql.Connection:
        return pymysql.connect(
            host = self.db_host,
            user = self.db_username,
            passwd = self.db_password,
            port = self.db_port
        )

@dataclass
class QueryParams:
    db_name: str
    table_name: str
    col_names: []
    index_key: str
    condition: str = ''


class SqlDataFrameMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams, chunk_size: int, offset: int) -> DataFrame:
        connection = self.connection.get_connection()
        sql = 'SELECT ' + ','.join(params.col_names) + ' FROM ' + params.db_name + '.' + params.table_name + ' ' + params.condition + ' LIMIT %d OFFSET %d'
        sql = sql % (chunk_size, offset)
        df = pd.read_sql_query(sql, connection)
        # df = df.set_index(params.index_key)
        return df

class SqlColumnInfoDataFrameMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    def map(self, params: QueryParams) -> DataFrame:
        sql = 'SELECT COLUMN_NAME , DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = "' + params.db_name + '" AND TABLE_NAME = "' + params.table_name + '"'
        return pd.read_sql_query(sql, connection.get_connection())


class IDataWriter:
    def write(self, params: QueryParams) -> None:
        raise NotImplemented


class ChunkedParquetWriter(IDataWriter):
    def __init__(self, mapper: SqlDataFrameMapper, path: str):
        self.mapper = mapper
        self.path = path

    def write(self, params: QueryParams, chunk_size: int = 1000000):
        offset = 0
        count = 1
        outdir = Path(self.path + '/' + params.db_name + '/' + params.table_name + '/')
        outdir.mkdir(parents=True, exist_ok=True)
        while True:
            df = self.mapper.map(params, chunk_size, offset)
            outfile = str(count) + '.parquet'
            df.to_parquet(outdir / outfile)
            count = count + 1
            offset += chunk_size
            if len(df) < chunk_size:
                break

    def read(self, params: QueryParams):
        datadir = Path(self.path + '/' + params.db_name + '/' + params.table_name + '/')
        full_df = pd.concat(
            pd.read_parquet(parquet_file)
            for parquet_file in datadir.glob('*.parquet')
        )
        return full_df.sort_values(params.index_key)



class IDataProcessor:
    def process(self, params: QueryParams):
        raise NotImplemented


class IDataTransformer:
    def transform(self, df: DataFrame) -> DataFrame:
        raise NotImplemented


class DateTimeStringTransformer(IDataTransformer):
    def transform(self, df: DataFrame) -> DataFrame:
        raise NotImplemented


class ChunkedDataProcessor(IDataProcessor):
    def __init__(self, chunk_size: int = 1000000):
        self.chunk_size = chunk_size

    # def process(self, params: QueryParams):


class DataProcessor:
    def __init__(self, writer: IDataWriter):
        self.writer = writer




class DataTypeMapper:
    def __init__(self, connection: IConnection):
        self.connection = connection

    # def map(self, dbname: str, tablename: str):

# class DataFrameRepository:

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
            ssh_password = self.ssh_password,
            ssh_username = self.ssh_username,
            remote_bind_address = (
                self.remote_bind_address, int(self.remote_bind_port)
            )
        )
        tunnel.start()

        pymysql = PyMysql(
            db_host = self.db_host,
            db_username = self.db_username,
            db_password = self.db_password,
            db_port = tunnel.local_bind_port
        )

        return pymysql.get_connection()

class CachedConnection(IConnection):
    def __init__(self, connection: IConnection):
        self.connection = connection

    def get_connection(self):
        if not hasattr(self, 'cached_connection') or self.cached_connection == None:
            self.cached_connection = self.connection.get_connection()

        return self.cached_connection


connection = CachedConnection(
    TunneledConnection(
        ssh_host = os.getenv('ssh_host'),
        ssh_username = os.getenv('ssh_username'),
        ssh_password = os.getenv('ssh_password'),
        ssh_port = int(os.getenv('ssh_port')),
        remote_bind_address = os.getenv('remote_bind_address'),
        remote_bind_port = int(os.getenv('remote_bind_port')),
        db_host = os.getenv('db_host'),
        db_username = os.getenv('db_user'),
        db_password = os.getenv('db_password')
))


mapper = SqlDataFrameMapper(connection)
writer = ChunkedParquetWriter(SqlDataFrameMapper(connection), 'data')


column_mapper = SqlColumnInfoDataFrameMapper(connection)
# params = QueryParams(
#     db_name='nanohub', table_name='jos_users', col_names = ['id', 'name', 'username', 'email'], index_key='id'
# )
# writer.write(params)
# print(writer.read(params))

params = QueryParams(
    db_name='nanohub', table_name='jos_tool_version', col_names = ['*'], index_key='id'
)
column_types = column_mapper.map(params)
print(column_types)
values = mapper.map(params, 10000000, 0)

df = column_types.loc[column_types['DATA_TYPE'] == 'datetime']
# print(df)
for index, row in df.iterrows():
    values[row['COLUMN_NAME']] = pd.to_datetime(values[row['COLUMN_NAME']],errors='coerce')

values.to_parquet('test.parquet')

df = pd.read_parquet('test.parquet')
print(df['unpublished'])

params = QueryParams(
    db_name='nanohub_metrics',
    table_name='toolstart',
    col_names = [
        'id', 'sessionid', 'orgtype', 'countryresident', 'countrycitizen', 'protocol', 'success', 'countryip', 'ip', 'host', 'user', 'tool', 'pid', 'domain', 'filesystem', 'execunit', 'walltime', 'cputime', 'error'
    ],
    index_key='id'
)

# writer.write(params)
# print(writer.read(params))

# df = mapper.map('nanohub', 'jos_users', 'id, name, username, email', 'id')
# print(df.head())
# df.to_parquet('data/users.parquet')
#
# df = mapper.map('nanohub', 'jos_tool_version', 'id,toolname,instance,title,description,fulltxt,version,revision,toolaccess,codeaccess,wikiaccess,state,released_by,exportControl,license,vnc_geometry,vnc_depth,vnc_timeout,vnc_command,mw,toolid,priority,params', 'id')
# print(df.head())
# df.to_parquet('data/tool_version.parquet')
#
# df = mapper.map('nanohub_metrics', 'toolstart', 'id,sessionid,orgtype,countryresident,countrycitizen,protocol,success,countryip,ip,host,user,tool,pid,domain,filesystem,execunit,walltime,cputime,error', 'id')
# print(df.head())
# df.to_parquet('data/toolstart.parquet')

# df = pd.read_parquet('output.parquet')
# print(df.head())