from pathlib import Path
from functools import reduce
import pandas as pd
import numpy as np
import os
from datetime import datetime
from IPython.display import display

from nanoHUB.application import Application
from nanoHUB.dataaccess.sql import SqlDataFrameMapper
from nanoHUB.dataaccess.sql import CachedConnection, TunneledConnection
from nanoHUB.rfm.model import LastUpdateRecord, TempUserDescriptors, UserDescriptors

from sqlalchemy import select
from sqlalchemy.orm import Session

application = Application.get_instance()
rfm_engine = application.new_db_engine('rfm_data')
nanohub_engine = application.new_db_engine('nanohub')
metrics_engine = application.new_db_engine('nanohub_metrics')

cache_dir = Path(Path(os.getenv('APP_DIR')), '.cache')


def get_connection():
    return CachedConnection(TunneledConnection(
        ssh_host = os.getenv('tunnel_ssh_host'),
        ssh_username = os.getenv('tunnel_ssh_username'),
        ssh_password = os.getenv('tunnel_ssh_password'),
        ssh_port = int(os.getenv('tunnel_ssh_port')),
        remote_bind_address = os.getenv('tunnel_remote_bind_address'),
        remote_bind_port = int(os.getenv('tunnel_remote_bind_port')),
        db_host = os.getenv('db_host'),
        db_username = os.getenv('db_user'),
        db_password = os.getenv('db_password')
    ))


def data_mapper(chunksize: int = 1000):
    return SqlDataFrameMapper(get_connection(), chunksize)


default_data_mapper = data_mapper()


def get_tool_version_df() -> pd.DataFrame:
    return pd.read_sql_query(
        "SELECT  toolname, instance FROM nanohub.jos_tool_version",
        nanohub_engine
    )


def new_toolstart_df() -> pd.DataFrame:
    df = pd.read_sql_query(
        "SELECT id, datetime, user, tool, walltime, cputime FROM nanohub_metrics.toolstart",
        nanohub_engine
    )
    df['datetime'] = pd.to_datetime(df['datetime'],errors='coerce')
    return df


def read_df(path: Path) -> pd.DataFrame:
    return pd.read_parquet(path)


def save_df(df, path: Path) -> None:
    df.to_parquet(path, compression='gzip')


def filter_nulls(df: pd.DataFrame, col_name: str) -> pd.DataFrame:
    df[col_name] = df[col_name].str.strip()
    df = df[~df[col_name].isna()]
    return df[df[col_name] != '']


def map_tool_instance(toolstart_df: pd.DataFrame, tool_version_df: pd.DataFrame) -> pd.DataFrame:
    toolstart_df['instance'] = toolstart_df['tool'].str.lower()

    tool_version_df['instance'].str.lower()
    tool_version_df['toolname'].str.lower()

    dummy = pd.DataFrame()
    dummy['toolname'] = tool_version_df['toolname'].drop_duplicates()
    dummy['instance'] = dummy['toolname']

    tool_version_df = pd.concat([dummy, tool_version_df], axis=0).drop_duplicates().reset_index(drop=True)

    df = pd.merge(toolstart_df, tool_version_df, how='left', left_on='instance', right_on='instance')[['user', 'toolname']]
    df = filter_nulls(df, 'user')
    df = filter_nulls(df, 'toolname')
    return df


def tool_counts(toolstart_df: pd.DataFrame, tool_version_df: pd.DataFrame) -> pd.DataFrame:
    df = map_tool_instance(toolstart_df, tool_version_df)
    return df.groupby(['user', 'toolname'])['toolname'].count().to_frame(name='tools_used_count').reset_index()


def max_min_simulation_datetimes(df: pd.DataFrame) -> pd.DataFrame:
    df = filter_nulls(df, 'user')
    df = df.groupby(['user']).agg(min_datetime=('datetime', np.min), max_datetime=('datetime', np.max)).reset_index()
    df.loc[df.min_datetime == '0000-00-00 00:00:00', 'min_datetime'] = '2000-01-01 00:10:10'
    return df


def simulation_lifetime(df: pd.DataFrame) -> pd.DataFrame:
    df = max_min_simulation_datetimes(df)
    df['sims_lifetime'] = (df['max_datetime'] - df['min_datetime']).dt.days
    # What happens to users who only used simulations for < 24hrs?
    # We assign 1 day to them.
    df.loc[df.sims_lifetime == 0, 'sims_lifetime'] = 1
    df.drop('min_datetime', axis=1, inplace=True)
    df.drop('max_datetime', axis=1, inplace=True)
    return df


def earliest_latest_simulations(df: pd.DataFrame) -> pd.DataFrame:
    df = max_min_simulation_datetimes(df)
    df = df.rename({'min_datetime': 'first_sim_date'}, axis=1)
    df = df.rename({'max_datetime': 'last_sim_date'}, axis=1)
    return df


def tools_used(toolstart_df: pd.DataFrame, tool_version_df: pd.DataFrame, delimiter: str = ',') -> pd.DataFrame:
    df = tool_counts(toolstart_df, tool_version_df)
    return df.groupby(['user']).toolname.agg([('tools_used_count', 'count'), ('tools_used_names', delimiter.join)]).reset_index()


def simulations_run_count(toolstart_df: pd.DataFrame, tool_version_df: pd.DataFrame) -> pd.DataFrame:
    df = tool_counts(toolstart_df, tool_version_df)
    df = df.rename({'tools_used_count': 'sims_count'}, axis=1)
    return df.groupby(['user']).sum().reset_index()


def sims_activity_days(df: pd.DataFrame) -> pd.DataFrame:
    df = df.groupby('user').agg(sims_activity_days=('user', 'count')).reset_index()
    return df


def update_last_toolstart_id(df: pd.DataFrame, connection):
    last_id = df.iloc[-1]["id"]
    now = datetime.now()
    formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
    sql = "INSERT INTO rfm_data.%s (last_processed_toolstart_id, last_processed_toolstart_id_updated)" % LastUpdateRecord.__tablename__
    sql = sql + " VALUES (%s, %s);"
    connection.execute(sql, (int(last_id), formatted_date))


def get_last_updated_toolstart_id(session):
    statement = select(LastUpdateRecord)
    result = session.execute(statement).scalars().all()
    if len(result) == 0:
        return 0
    return result[0].last_processed_toolstart_id


def merge_tool_data(toolstart_df: pd.DataFrame, tool_version_df: pd.DataFrame, delimiter: str = ',') -> pd.DataFrame:
    simulation_lifetime_df = simulation_lifetime(toolstart_df)
    tools_used_df = tools_used(toolstart_df, tool_version_df)
    simulations_count_df = simulations_run_count(toolstart_df, tool_version_df)
    earliest_latest_simulations_df = earliest_latest_simulations(toolstart_df)
    sims_activity_days_df = sims_activity_days(toolstart_df)

    df_merged = reduce(lambda left,right: pd.merge(left, right, on=['user'], how='outer'), [
        simulation_lifetime_df,
        tools_used_df,
        simulations_count_df,
        earliest_latest_simulations_df,
        sims_activity_days_df
    ])
    # display(df_merged)
    return df_merged


def update_user_info(engine):
    sql1 = '''
    INSERT INTO rfm_data.%s (id, username, name, email, last_visit_date, registration_date, lifetime_days)
    SELECT id, username, name, email, lastvisitDate, registerDate, timestampdiff(DAY, registerDate, lastvisitDate)
    FROM nanohub.jos_users
    WHERE NOT EXISTS (SELECT 1 FROM rfm_data.user_descriptor WHERE rfm_data.user_descriptor.id = nanohub.jos_users.id)
    '''
    sql1 = sql1 % (UserDescriptors.__tablename__)
    sql2 = '''
    UPDATE rfm_data.%s INNER JOIN nanohub.jos_users
        ON rfm_data.user_descriptor.id = nanohub.jos_users.id
    SET rfm_data.user_descriptor.lifetime_days = timestampdiff(DAY, nanohub.jos_users.registerDate, nanohub.jos_users.lastvisitDate)
    WHERE rfm_data.user_descriptor.last_visit_date != nanohub.jos_users.lastvisitDate
    '''
    sql2= sql2 % (UserDescriptors.__tablename__)

    with engine.begin() as connection:
        with connection.begin() as transaction:
            connection.execute(sql1)
            connection.execute(sql2)


def update_tool_info(engine, toolstart_df, tool_version_df):
    sql = '''
    UPDATE rfm_data.%s AS final JOIN rfm_data.%s AS temp
    ON final.username = temp.user
    SET
        final.sims_count = temp.sims_count,
        final.sims_lifetime = temp.sims_lifetime,
        final.sims_activity_days = temp.sims_activity_days,
        final.tools_used_count = temp.tools_used_count,
        final.tools_used_names = temp.tools_used_names,
        final.last_sim_date = temp.last_sim_date,
        final.first_sim_date = temp.first_sim_date
    '''
    sql = sql % (UserDescriptors.__tablename__, TempUserDescriptors.__tablename__)
    session = Session(engine, future=True)
    last_updated_toolstart_id = get_last_updated_toolstart_id(session)
    session.close()

    toolstart_df = toolstart_df[toolstart_df.id > last_updated_toolstart_id]

    if len(toolstart_df) > 0:
        merged_df = merge_tool_data(toolstart_df, tool_version_df)
        merged_df.to_sql(TempUserDescriptors.__tablename__, engine, if_exists='replace')

        with engine.begin() as connection:
            update_last_toolstart_id(toolstart_df, connection)
            connection.execute(sql)


pd.options.mode.chained_assignment = None

toolstart_path = Path(cache_dir, 'toolstart_1')
toolstart_df = read_df(toolstart_path)
tool_version_df = get_tool_version_df()


update_user_info(rfm_engine)
update_tool_info(rfm_engine, toolstart_df, tool_version_df)
