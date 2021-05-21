from sql import *
from cache import *
from transformers import *
from . import logger
import os
from dotenv import load_dotenv

load_dotenv()

connection = CachedConnection(TunneledConnection(
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

etl = ETL(
    SqlDataFrameMapper(connection),
    DataTransformers([DateTimeConvertor()]),
    CachedDataLoader(ParquetFiles(), '.cache', logger())
)

etl(QueryParams(
    db_name='nanohub', table_name='jos_users', col_names = ['id', 'name', 'username', 'email'], index_key='id'
))
etl(QueryParams(
    db_name='nanohub', table_name='jos_tool_version', col_names = ['*'], index_key='id'
))
etl(QueryParams(
    db_name='nanohub_metrics', table_name='toolstart', col_names = ['*'], index_key='id'
))