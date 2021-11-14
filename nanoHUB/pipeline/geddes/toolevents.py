from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import QueryString, new_df, get_default_s3_client, save_df
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
from_date = datetime.date(2012,12,25)
end = datetime.date.today()

while from_date < end:
    nextday = from_date + datetime.timedelta(days = 1)
    df = new_df(query, from_date, nextday, nanohub_metrics_db)
    from_date = nextday
    save_df(s3_client, df, bucket_name, '%s/%s/%s' % (query.db_name, query.table_name, nextday))




