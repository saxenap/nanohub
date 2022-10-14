# Created by saxenap at 10/13/22

from pathlib import Path
from functools import reduce
import pandas as pd
import numpy as np
import os
from datetime import datetime
from nanoHUB.logger import logger as log

from nanoHUB.application import Application
from nanoHUB.dataaccess.lake import create_default_s3mapper
application = Application.get_instance()
rfm_engine = application.new_db_engine('rfm_data')
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')

cache_dir = Path(Path(os.getenv('APP_DIR')), '.cache')



nanohub_engine.connect().execution_options(
    stream_results=True
)

metrics_engine.connect().execution_options(
    stream_results=True
)
raw_geddes_mapper = create_default_s3mapper(application, 'nanohub.raw')

for chunk_users_df in pd.read_sql(
        "SELECT id, username, registerDate, lastvisitDate FROM nanohub.jos_users ORDER BY id",
        nanohub_engine,
        chunksize=1000
):
    print(chunk_users_df)
    print(f"Got dataframe w/{len(chunk_users_df)} rows")

    raw_geddes_mapper.save_as_parquet(chunk_users_df, 'nanohub/jos_users')
    raw_geddes_mapper.save_as_csv(chunk_users_df, 'nanohub/jos_users/by_registration_day')
    exit(1)

if __name__ == '__main__':
    process_sql_using_pandas()

exit(1)

sql = '''
SELECT COUNT(DISTINCT tool_versions.toolname) as count_tools,
       GROUP_CONCAT(DISTINCT tool_versions.toolname SEPARATOR ', ') as names_tools,
       summary.username
    FROM nanohub_metrics.toolevents AS events
    INNER JOIN nanohub.jos_tool_version as tool_versions
        ON tool_versions.instance = events.tool
    INNER JOIN rfm_data.toolevents_summary_2 AS summary
        ON summary.username = events.user
    GROUP BY summary.username
;
'''

df = pd.read_sql(sql, metrics_engine)
df.to_parquet(Path(cache_dir, 'toolevents/tools.parquet'), compression='gzip')
print(df)
