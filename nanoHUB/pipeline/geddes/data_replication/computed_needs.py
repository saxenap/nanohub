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
app_dir = '/Users/saxenap/Documents/Dev/nanoHUB/nanoHUB-analytics'
datadir = app_dir + '/.cache/'
file_path = datadir + 'registered_users.csv'

sql_query = ''' 
SELECT 
    id, name, username, email, registerDate, lastvisitDate 
FROM nanohub.jos_users
WHERE username != ''
AND username NOT IN ('gridstat', 'hubrepo')
'''

# users_df = pd.read_sql_query(sql_query, nanohub_engine)
# # print(users_df)
# print(len(users_df))
# users_df = users_df.reset_index()
# print(len(users_df))
# users_df.to_csv(file_path)

users_df = pd.read_csv(file_path)

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

usernames_list = users_df['username'].tolist()

for i in range(0, len(usernames_list), 100):
    usernames = usernames_list[i:i+100]
    placeholders = ','.join(['%s'] * len(usernames))
    sql_query = sql_query.format(users=placeholders)
    # print(sql_query)
    with nanohub_engine.begin() as connection:
        # print(tuple(usernames))
        connection.execute(sql_query, tuple(usernames))
        print("%d users updated so far." % (i + len(usernames)))

