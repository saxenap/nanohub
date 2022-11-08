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
import pymysql
from sqlalchemy import exc

application = Application.get_instance()
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')
s3_client = get_default_s3_client(application)
# raw_mapper = S3FileMapper(s3_client, inparams.bucket_name)

parser = argparse.ArgumentParser(
    description='Designed for nanoHUB.org')

parser.add_argument('--cache_dir', help='specific task', action='store')
parser.add_argument('--chunk_size', help='specific task', action='store', type=int)
parser.add_argument('--refresh_cache', help='specific task', action='store_true')
parser.add_argument('--no_refresh_cache', dest='refresh_cache', action='store_false')
parser.set_defaults(refresh_cache=True)


inparams = parser.parse_args()

file_path = inparams.cache_dir.rstrip('/') + '/registered_users.csv'

usernames_query_str = '''
SELECT 
   DISTINCT user AS username
FROM nanohub_metrics.toolevents events
WHERE user != ''
AND events.user NOT IN (SELECT username FROM ANALYTICS_derived_data.simulations)
LIMIT {} OFFSET {}
;
'''
# sql_query = '''
# SELECT
#     id, username
# FROM nanohub.jos_users users
# WHERE users.username != ''
# AND users.username NOT IN ('gridstat', 'hubrepo')
# AND users.username NOT REGEXP '^[-]'
# AND users.id NOT IN (SELECT user_id FROM ANALYTICS_derived_data.simulations)
# ORDER BY id
# ;
# '''
# AND users.username NOT REGEXP '^[-]'
# if inparams.refresh_cache == True:
#     print("Refreshing cache from fresh user data.")
#     event_users_df = pd.read_sql_query(sql_query_1, nanohub_engine)
#     # print(users_df)
#     print(len(event_users_df))
#     event_users_df = event_users_df.reset_index()
#     print("Writing users list to %s" % file_path)
#     event_users_df.to_csv(file_path)

# sql_query_2 = '''
# SELECT username FROM ANALYTICS_derived_data.simulations;
# '''
# sims_users_df = pd.read_sql_query(sql_query_2, nanohub_engine)
#
# df_merged = event_users_df.merge(sims_users_df.drop_duplicates(), on=['username'],
#                    how='left', indicator=True)
# df_not_incommon = df_merged.query("_merge == 'left_only'")
# print(df_not_incommon)
# print(len(df_not_incommon))

# usernames_list = df_not_incommon['username'].tolist()
# print(len(usernames_list))
# print(df_not_incommon.tail())

# users_df = pd.read_csv(file_path)
# print(len(users_df))

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

# usernames_list = list(set(usernames_list))
# print("Number of usernames: %d" % len(usernames_list))
chunk_size = inparams.chunk_size
offset = 0
all_users = 0
while True:
    print("offset = %d" % offset)
    usernames_query_formatted = usernames_query_str.format(chunk_size, offset)
    print(usernames_query_formatted)
    offset = offset + chunk_size
    usernames_df = pd.read_sql(
        usernames_query_formatted, nanohub_engine
    )
    usernames = usernames_df['username'].tolist()

    print(usernames)
    if len(usernames) <= 0:
        break

    placeholders = ','.join(['%s'] * len(usernames))
    sql_query = sql_query.format(users=placeholders)
    with nanohub_engine.begin() as connection:
        connection.execute(sql_query, tuple(usernames))
    all_users = all_users + len(usernames)
    print("%d users updated" % len(usernames))


# for i in range(0, len(usernames_list), chunk_size):
#     usernames = usernames_list[i:i+chunk_size]
#     placeholders = ','.join(['%s'] * len(usernames))
#     sql_query = sql_query.format(users=placeholders)
#     df = pd.read_sql(sql_query, nanohub_engine, tuple(usernames))
#     # print(sql_query)
#     with nanohub_engine.begin() as connection:
#         print(tuple(usernames))
#         print(i)
#         print(i+chunk_size)
#         connection.execute(sql_query, tuple(usernames))
        # print(connection.execute("SELECT last_insert_id() FROM ANALYTICS_derived_data.simulations;"))

    # print("%d existing users found." % existing_users)
    # print("%d users updated so far." % (new_users))
