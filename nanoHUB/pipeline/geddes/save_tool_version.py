from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import map_for_all, QueryStringForAll, get_default_s3_client
import datetime


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')

s3_client = get_default_s3_client(application)

query = QueryStringForAll(
    'nanohub',
    'jos_tool_version',
    ['*'],
    ['released', 'unpublished']
)
bucket_name = 'nanohub.raw'
map_for_all(
    query, nanohub_metrics_db, s3_client, bucket_name
)