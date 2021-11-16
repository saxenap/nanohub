from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import map, QueryString, get_default_s3_client
import datetime


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')

s3_client = get_default_s3_client(application)

query = QueryString(
    'nanohub_metrics',
    'toolevents',
    'start',
    'start',
    ['*'],
    ['start', 'finish']
)
bucket_name = 'nanohub.raw'
from_date = datetime.date(2002,7,3)
end = datetime.date.today()

map(
    query, nanohub_metrics_db, s3_client, bucket_name, from_date
)

