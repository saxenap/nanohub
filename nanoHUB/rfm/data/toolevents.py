from pathlib import Path
from functools import reduce
import pandas as pd
import numpy as np
import os
from datetime import datetime

from nanoHUB.application import Application

application = Application.get_instance()
rfm_engine = application.new_db_engine('rfm_data')
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')

cache_dir = Path(Path(os.getenv('APP_DIR')), '.cache')

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
