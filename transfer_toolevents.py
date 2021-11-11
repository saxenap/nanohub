from pathlib import Path
from functools import reduce
import pandas as pd
import numpy as np
import os, sys
from google.cloud import storage
import time
import gcsfs


from datetime import datetime

from nanoHUB.application import Application
from nanoHUB.rfm.model import LastUpdateRecord, TempUserDescriptors, UserDescriptors

from sqlalchemy import select
from sqlalchemy.orm import Session
import time

application = Application.get_instance()
rfm_engine = application.new_db_engine('rfm_data')
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')

APP_DIR="/home/saxenap/nanohub"
CACHE_DIR = Path(APP_DIR, '.cache')

def new_toolevents_df(last_inserted_id: int, chunksize: int) -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT entryID, source, job, superjob, sessnum, event, start, finish, user, tool, walltime, cputime, latitude, longitude, city, region, countryLong, countryShort FROM nanohub_metrics.toolevents WHERE toolevents.entryID > %d ORDER BY entryID LIMIT %d" % (last_inserted_id, chunksize),
        metrics_engine
    )
    df['datetime'] = pd.to_datetime(df['start'],errors='coerce')
    df['datetime'] = pd.to_datetime(df['finish'],errors='coerce')
    return df


def save_df(df, bucket_name: str, folder_name: str) -> None:
    timestr = time.strftime("%Y%m%d-%H%M%S")
    full_path = 'gs://%s/%s/%s.parquet.gzip' % (bucket_name, folder_name, timestr)
    print('Saving dataframe to google now (%s)' % (full_path))
    # with fs.open(full_path) as f:

    df.to_parquet(full_path, compression='gzip', storage_options={"token": "nanohub-320518-a9f4878b9ea2.json"})


def get_last_id(path: Path) -> int:
    try:
        with open(path, 'r') as f:
            last_id = int(f.read())
    except (IOError, ValueError):
        last_id = 0

    print("Reading last id (%d)" % (last_id))
    return last_id


def get_last_id_by_datetime_file(directory_path: Path) -> int:
    df = pd.read_parquet(full_path, storage_options={"token": "nanohub-320518-a9f4878b9ea2.json"})
    next_id = df['entryID'].iloc[-1]


def save_last_id(path: Path, last_id: int):
    print("Saving last id (%d)" % (last_id))
    with open(path, 'w') as f:
        f.write(str(last_id))


chunksize = 10000000
last_id_file_path = Path(CACHE_DIR, 'toolevents_last_id')

while True:
    last_id = get_last_id(last_id_file_path)
    df = new_toolevents_df(last_id, chunksize)
    if df.empty: break
    save_df(df, 'nanohub_metrics', 'toolevents')
    next_id = df['entryID'].iloc[-1]
    save_last_id(last_id_file_path, next_id)

print('done')



