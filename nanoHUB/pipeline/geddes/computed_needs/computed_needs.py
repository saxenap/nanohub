# Created by saxenap at 10/13/22

from datetime import datetime, timedelta, date
import logging
import time
import argparse
import tempfile
import os

import botocore
import pandas as pd
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.dataaccess.lake import S3FileMapper
from nanoHUB.logger import logger as log
from botocore.exceptions import ClientError


application = Application.get_instance()
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')
s3_client = get_default_s3_client(application)
# raw_mapper = S3FileMapper(s3_client, inparams.bucket_name)

processed_mapper = S3FileMapper(s3_client, ClusteringConfiguration().bucket_name_processed)

# app_dir = os.environ['APP_DIR']
app_dir = '/'
cache_dir = app_dir + '/.cache/'


def save_users(df: pd.DataFrame, file_path: str):
    df.to_csv(file_path)

def get_users_from_db(engine, from_date: datetime, to_date: datetime):
    sql_query = ''' 
    SELECT 
        id, name, username, email, registerDate, lastvisitDate 
    FROM nanohub.jos_users
    WHERE username != ''
    AND username NOT IN ('gridstat', 'hubrepo')
    AND registerDate BETWEEN '{0}' AND '{1}'
'''
    formatted_query = sql_query.format(from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'))
    print(formatted_query)
    df = pd.read_sql(formatted_query, engine, parse_dates={'registerDate': {'format': '%Y-%m-%d %H:%M:%S'}, 'lastvisitDate': {'format': '%Y-%m-%d %H:%M:%S'}})
    print("Users found from %s to %s: %d" % (from_date.strftime('%Y-%m-%d'), to_date.strftime('%Y-%m-%d'), len(df)))
    return df

def import_users(file_path: str, use_cache: bool = False):
    if use_cache == False:
        users_df = get_users_from_db()
        save_users(users_df, file_path)

    users_df = pd.read_csv(file_path)
    print("Number of users imported: %d" % len(users_df))

    return users_df


def save_details(users_df: pd.DataFrame, engine, chunk_size: int):
    sql_query = """
    INSERT INTO ANALYTICS_derived_data.simulations
    (username,
     user_id,
     tool_count,
     session_count,
     sim_count,
     earliest_sim,
     latest_sim,
     active_duration,
     sim_lifetime,
     last_entryId,
     num_sim_active_days)
    SELECT DISTINCT rollup.user AS username,
                    rollup.user_id AS user_id,
                    COUNT(DISTINCT rollup.tool_name) AS tool_count,
                    (SELECT COUNT(*) FROM nanohub_metrics.toolstart WHERE user = rollup.user) AS session_count,
                    (SELECT COUNT(*) FROM nanohub_metrics.toolevents WHERE user = rollup.user) AS sim_count,
                    MIN(rollup.earliest_sim) AS earliest_sim,
                    MAX(rollup.latest_sim) AS latest_sim,
                    DATEDIFF(rollup.lastvisitDate, rollup.registerDate) AS active_duration,
                    DATEDIFF(MAX(rollup.latest_sim), MIN(rollup.earliest_sim)) AS sim_lifetime,
                    MAX(rollup.max_entryId) AS last_entryId,
                    (SELECT COUNT(DISTINCT DATE_FORMAT(start, '%%Y-%%m-%%d')) FROM nanohub_metrics.toolevents  WHERE user = rollup.user) AS num_sim_active_days
    FROM (SELECT DISTINCT events.user        AS user,
                          MIN(events.start)  AS earliest_sim,
                          MAX(events.start)  AS latest_sim,
                          COUNT(*)  AS tool_name,
                          COUNT(DISTINCT events.entryID) AS tool_sim_count,
    #             COUNT(DISTINCT starts.id) AS tool_session_count,
                          MAX(events.entryID) AS max_entryId,
                          users.id           AS user_id,
                          users.registerDate AS registerDate,
                          users.lastvisitDate AS lastvisitDate
          FROM nanohub_metrics.toolevents events
                 INNER JOIN nanohub.jos_tool_version versions
                            ON versions.instance = events.tool
                 INNER JOIN nanohub.jos_users users
                            ON users.username = events.user
          WHERE events.user != ''
            AND events.user IN ({users})
          GROUP BY events.user, versions.toolname
         ) AS rollup
    WHERE  rollup.user != ''
    GROUP BY rollup.user
    ;
    """
    usernames = users_df['username'].tolist()
    if len(usernames) > 0:
        placeholders = ','.join(['%s'] * len(usernames))
        sql_query = sql_query.format(users=placeholders)
        with engine.begin() as connection:
            connection.execute(sql_query, tuple(usernames))
        print("%d users processed" % len(usernames))
    else:
        print("No usernames found to process")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--date_probe_range',
                        help='date range in isoformat. For example, 2018-01-01_2018-05-01',
                        action='store', default='latest')
    # parser.add_argument('--query_string', help='Query string', action='store')
    parser.add_argument('--chunk_size', help='Chunk size for number of users', action='store', default=100, type=int)
    # parser.add_argument('--use_cache', help='Use cache', action='store')
    # parser.add_argument('--cache_dir_path', help='Relative path of cache dir', action='store')
    inparams = parser.parse_args()

    application = Application.get_instance()
    nanohub_engine = application.new_db_engine('nanohub')
    metrics_engine = application.new_db_engine('nanohub_metrics')

    # app_dir = os.environ['APP_DIR']
    # # cache_dir = app_dir + '/' + inparams.cache_dir_path
    # file_path = cache_dir +

    inparams.start_date, inparams.end_date = inparams.date_probe_range.split('_')

    users_df = get_users_from_db(nanohub_engine, datetime.fromisoformat(inparams.start_date), datetime.fromisoformat(inparams.end_date))
    save_details(users_df, nanohub_engine, inparams.chunk_size)


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print("Time:", end - start)