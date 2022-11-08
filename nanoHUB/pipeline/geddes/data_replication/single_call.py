# Created by saxenap at 10/13/22
from datetime import datetime, timedelta, date
import logging
import time
import argparse
import tempfile

import botocore
import pandas as pd
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.dataaccess.lake import S3FileMapper
from nanoHUB.logger import logger as log
from botocore.exceptions import ClientError


def daterange(start_date: datetime, end_date: datetime):
    for n in range(int((end_date - start_date).days)):
        single_date = start_date + timedelta(n)
        yield single_date

def get_by_day_since(engine, query: str, start_date: datetime, end_date: datetime, mapper, path: str, date_columns, skip_existing: int):
    for from_date in daterange(start_date, end_date):
        to_date = from_date + timedelta(days=1)
        formatted_query = query.format(from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
        # print(formatted_query)
        full_path = path + '/' + str(from_date.year) + '/' + str(from_date.month) + '/' + str(from_date.date()) + '.parquet.gzip'
        # print(full_path)
        if mapper.exists(full_path):
            if skip_existing == 1:
                # print("File path %s already exists. Skipping." % full_path)
                continue
            # print("Overwriting file path %s." % full_path)
        df = pd.read_sql(formatted_query, engine, parse_dates={'start': {'format': '%Y-%m-%d %H:%M:%S'}, 'finish': {'format': '%Y-%m-%d %H:%M:%S'}})
        # print("%s now uploading." % full_path)
        try:
            mapper.upload_file(df, full_path, compression='gzip')
            # print("Uploaded: %s" % (full_path))
        except ClientError as e:
            print("Error uploading: %s (%s)" % (full_path, str(e)))





# def save_to_geddes(mapper, path, df, date_range: str, file_extension:str):
#     # if file_extension == 'csv':
#     #     full_path = path + '/' + date_range + '.csv'
#     #     mapper.load_file(df, full_path)
#     # elif file_extension == 'parquet':
#     #     full_path = path + '/' + date_range + '.parquet'
#     #     mapper.load_file(df, full_path)
#     # else:
#     #     raise RuntimeError('Unknown desired file extension %s' % file_extension)


def single_call():
    parser = argparse.ArgumentParser()
    parser.add_argument('--bucket_name', help='bucket name in Geddes', action='store', default=ClusteringConfiguration().bucket_name_raw)
    parser.add_argument('--object_path', help='object path inside the bucket in Geddes', action='store')
    parser.add_argument('--save_as', help='desired file extension', action='store', default='parquet')
    parser.add_argument('--date_probe_range',
                        help='date range. For example, 2018-1-1_2018-5-1',
                        action='store', default='latest')
    # parser.add_argument('--query_string', help='Query string', action='store')
    parser.add_argument('--database_name', help='Database name', action='store')
    parser.add_argument('--table_name', help='Database table name', action='store')
    parser.add_argument('--column_names', help='Comma separated list of columns in the database table that you want replicated', action='store')
    parser.add_argument('--date_column', help='Name of the date column', action='store')
    parser.add_argument('--date_columns', help='comma separated list of all the date columns', action='store')
    parser.add_argument('--skip_existing', help='Skip overwriting a file if it already exists.', action='store', nargs='?', type=int, const=1, default=0)
    inparams = parser.parse_args()

    application = Application.get_instance()
    nanohub_engine = application.new_db_engine('nanohub')
    metrics_engine = application.new_db_engine('nanohub_metrics')
    s3_client = get_default_s3_client(application)
    raw_mapper = S3FileMapper(s3_client, inparams.bucket_name)
    # nanohub_engine = ''
    # raw_mapper = ''

    inparams.start_date, inparams.end_date = inparams.date_probe_range.split('_')

    query_string = "SELECT " + inparams.column_names + " FROM " + inparams.database_name + "." + inparams.table_name + " WHERE " + inparams.date_column + ">='{0}' AND " + inparams.date_column + "<'{1}'"


    get_by_day_since(
        nanohub_engine,
        query_string,
        datetime.fromisoformat(inparams.start_date),
        datetime.fromisoformat(inparams.end_date),
        raw_mapper,
        inparams.object_path,
        inparams.date_columns.split(','),
        inparams.skip_existing
    )

        # save_to_geddes(raw_mapper, inparams.object_path, df, inparams.date_probe_range, inparams.save_as)

if __name__ == '__main__':
    start = time.time()
    single_call()
    end = time.time()
    print("Time:", end - start)
# users_df = pd.read_sql_query(sql_query, nanohub_engine)
# file_path = 'nanohub/jos_users.csv'
# raw_mapper.save_as_csv(users_df, file_path, index=None)