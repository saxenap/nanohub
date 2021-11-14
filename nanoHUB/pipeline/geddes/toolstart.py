from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import map, QueryString, get_default_s3_client
import datetime


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')

s3_client = get_default_s3_client(application)

query = QueryString(
    'nanohub_metrics',
    'toolstart',
    'datetime',
    'datetime',
    ['*'],
    ['datetime']
)
bucket_name = 'nanohub.raw'
from_date = datetime.date(2012,1,1)
end = datetime.date.today()

map(
    query, nanohub_metrics_db, s3_client, bucket_name, from_date
)


