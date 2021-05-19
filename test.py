from nanoHUB.dataaccess.sql import *
from nanoHUB.dataaccess.common import *
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

repository = SqlDataRepository(SqlDataFrameMapper(connection), ColumnInfoMapper(connection))

params = QueryParams(
    db_name='nanohub', table_name='jos_tool_version', col_names = ['*'], index_key='id'
)
for x in repository.read(params):
    print(x.get_col_info())