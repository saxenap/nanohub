from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import save_df, new_df, QueryString, get_default_s3_client
import datetime
import argparse
import logging
from pprint import pformat

parser = argparse.ArgumentParser(
    description='Generate nanohub_metrics.toolevents by year'
)

parser.add_argument('--year', dest='year', help='specific year',
                    action='store')
parser.add_argument('--log_level', help='logging level (INFO, DEBUG etc)',
                    action='store', default='INFO')

parser.add_argument('--bucket_name', help='bucket name in Geddes', action='store')


inparams = parser.parse_args()

numeric_level = getattr(logging, inparams.log_level.upper(), 10)
logging.basicConfig(level=numeric_level, format='%(message)s')

logging.debug(pformat(vars(inparams)))


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')

s3_client = get_default_s3_client(application)


year = int(inparams.year)
from_date = datetime.date(year,1,1)
to_date = datetime.date(year,7,1)
query = QueryString(
    'nanohub_metrics',
    'toolevents',
    'start',
    'start',
    ['*'],
    ['start', 'finish']
)

df = new_df(
    query, from_date, to_date, nanohub_metrics_db
)
from_date_str = from_date.strftime('%Y-%m-%d')
to_date_str = to_date.strftime('%Y-%m-%d')
save_df(s3_client, df, inparams.bucket_name, '%s/%s/by_semester/%s_%s' % (query.db_name, query.table_name,from_date_str, to_date_str))

from_date = datetime.date(year,7,2)
to_date = datetime.date(year,12,31)
query = QueryString(
    'nanohub_metrics',
    'toolevents',
    'start',
    'start',
    ['*'],
    ['start', 'finish']
)

df = new_df(
    query, from_date, to_date, nanohub_metrics_db
)
from_date_str = from_date.strftime('%Y-%m-%d')
to_date_str = to_date.strftime('%Y-%m-%d')
save_df(s3_client, df, inparams.bucket_name, '%s/%s/by_semester/%s_%s' % (query.db_name, query.table_name,from_date_str, to_date_str))