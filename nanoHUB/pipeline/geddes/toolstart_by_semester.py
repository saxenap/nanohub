from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import save_df, new_df, QueryString, get_default_s3_client
from nanoHUB.dataaccess.lake import SemesterMapper, Semesters
from nanoHUB.configuration import ClusteringConfiguration
from datetime import datetime
import argparse


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub_metrics')
bucket_name = ClusteringConfiguration().bucket_name_raw
s3_client = get_default_s3_client(application)

semesters = [Semesters.fall, Semesters.spring]

query = QueryString(
    'nanohub_metrics',
    'toolstart',
    'datetime',
    'datetime',
    ['*'],
    ['datetime']
)

current_year = datetime.now().year
for year in range(2002, current_year + 1):
    from_date = Semesters().get_fall_begin(year)
    to_date = Semesters().get_fall_end(year)
    df_fall = new_df(
        query, from_date, to_date, nanohub_metrics_db
    )
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')
    save_df(s3_client, df_fall, bucket_name, '%s/%s/by_semester/%s_%s' % (query.db_name, query.table_name,from_date_str, to_date_str))

    from_date = Semesters().get_spring_begin(year)
    to_date = Semesters().get_spring_end(year)
    df_fall = new_df(
        query, from_date, to_date, nanohub_metrics_db
    )
    from_date_str = from_date.strftime('%Y-%m-%d')
    to_date_str = to_date.strftime('%Y-%m-%d')
    save_df(s3_client, df_fall, bucket_name, '%s/%s/by_semester/%s_%s' % (query.db_name, query.table_name,from_date_str, to_date_str))

# parser = argparse.ArgumentParser(
#     description='Generate nanohub_metrics.toolevents by year'
# )
#
# parser.add_argument('--year', dest='year', help='specific year',
#                     action='store')
# parser.add_argument('--log_level', help='logging level (INFO, DEBUG etc)',
#                     action='store', default='INFO')
#
# parser.add_argument('--bucket_name', help='bucket name in Geddes', action='store')
#
#
# inparams = parser.parse_args()
#
# numeric_level = getattr(logging, inparams.log_level.upper(), 10)
# logging.basicConfig(level=numeric_level, format='%(message)s')
#
# logging.debug(pformat(vars(inparams)))