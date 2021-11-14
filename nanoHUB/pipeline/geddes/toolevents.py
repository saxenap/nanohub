from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import map, QueryString, new_df, get_default_s3_client, save_df
import datetime


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')

s3_client = get_default_s3_client()

query = QueryString(
    'nanohub_metrics',
    'toolevents',
    'start',
    'start'
)
bucket_name = 'nanohub.raw'
from_date = datetime.date(2012,1,1)
end = datetime.date.today()

map(
    query, nanohub_metrics_db, s3_client, bucket_name, from_date
)


