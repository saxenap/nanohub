from nanoHUB.dataaccess.sql import *
from nanoHUB.dataaccess.cache import *
from nanoHUB.dataaccess.transformers import *
from nanoHUB.logger import logger
import os, logging
from dotenv import load_dotenv
load_dotenv('nanoHUB/.env')

connection = CachedConnection(TunneledConnection(
    ssh_host = os.getenv('tunnel_ssh_host'),
    ssh_username = os.getenv('tunnel_ssh_username'),
    ssh_password = os.getenv('tunnel_ssh_password'),
    ssh_port = int(os.getenv('tunnel_ssh_port')),
    remote_bind_address = os.getenv('tunnel_remote_bind_address'),
    remote_bind_port = int(os.getenv('tunnel_remote_bind_port')),
    db_host = os.getenv('db_host'),
    db_username = os.getenv('db_user'),
    db_password = os.getenv('db_password')
))

logger = logger()
logger.setLevel(logging.DEBUG)

etl = ETL(
    SqlDataFrameMapper(connection),
    DataTransformers([DateTimeConvertor()]),
    CachedDataLoader(ParquetFiles(True), '../../../.cache', logger)
)


# users = etl(QueryParams(
#     db_name='nanohub', table_name='jos_users', col_names = ['id', 'name', 'username', 'email', 'lastvisitDate', 'registerDate'], index_key='id'
# ))
# print('user data complete.')
#
# tool_versions = etl(QueryParams(
#     db_name='nanohub', table_name='jos_activity_logs', col_names = ['*'], index_key='id'
# ))
# print('jos_activity_logs complete.')

# jos_shibboleth_sessions = etl(QueryParams(
#     db_name='nanohub', table_name='jos_shibboleth_sessions', col_names = ['*'], index_key='id'
# ))
# print('jos_shibboleth_sessions complete.')
# print(jos_shibboleth_sessions)

# sessionlog_metrics = etl(QueryParams(
#     db_name='nanohub_metrics', table_name='sessionlog_metrics', col_names = ['*'], index_key='id'
# ))
# print('sessionlog_metrics complete.')


# tool_versions = etl(QueryParams(
#     db_name='nanohub', table_name='jos_tool_version', col_names = ['*'], index_key='id'
# ))
# print('toolversions complete.')

# tools = etl(QueryParams(
#     db_name='nanohub_metrics', table_name='tools', col_names = ['*'], index_key='tool'
# ))
# print('tools complete.')
toolstarts = etl(QueryParams(
    db_name='nanohub_metrics', table_name='toolstart', col_names = ['*'], index_key='id'
))
print('toolstarts complete.')
# toolevents = etl(QueryParams(
#     db_name='nanohub_metrics', table_name='toolevents', col_names = ['*'], index_key='entryID'
# ))
# print('toolevents complete.')
# logins = etl(QueryParams(
#     db_name='nanohub_metrics', table_name='userlogin', col_names = ['*'], index_key='id'
# ))
# print('logins complete.')
# print(toolstarts)

# table_info = SqlTableInfo(connection)
# print(table_info.get_primary_key_for('nanohub_metrics', 'userlogin'))