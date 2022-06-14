import logging

import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from io import BytesIO, StringIO
import boto3
from nanoHUB.application import Application
import botocore.client as s3client
from nanoHUB.pipeline.geddes.data import get_default_s3_client, read_all
from nanoHUB.configuration import ClusteringConfiguration, DataLakeConfiguration
import re


@dataclass
class QueryString:
    db_name: str
    table_name: str
    from_col_name: str
    to_col_name: str
    col_names: []
    datetime_cols: []

    def make_query(self, from_date: datetime, to_date: datetime) -> str:
        sql = '''
        SELECT %s FROM %s.%s WHERE %s >= '%s 00:00:00' AND %s < '%s 00:00:00';
        '''.strip()

        return sql % (
            ','.join(self.col_names),
            self.db_name,
            self.table_name,
            self.from_col_name,
            from_date,
            self.to_col_name,
            to_date
        )

    def get_datetime_cols(self) -> []:
        return self.datetime_cols


def new_df(query: QueryString, from_date: datetime, to_date: datetime, engine):
    print(query.make_query(from_date, to_date))
    df = pd.read_sql_query(query.make_query(from_date, to_date), engine)

    for col_name in query.datetime_cols:
        df[col_name] = pd.to_datetime(df[col_name],errors='coerce')

    return df


def get_default_s3_client(application) -> s3client:

    return get_s3_client(
        'https://' + application.get_config_value('geddesapi.endpoint') + ':443',
        application.get_config_value('geddesapi.access_key'),
        application.get_config_value('geddesapi.secret_key')
    )


def get_s3_client(endpoint_url: str, access_key: str, secret: str) -> s3client:

    boto_session = boto3.session.Session(
        aws_access_key_id = access_key,
        aws_secret_access_key = secret
    )

    return boto_session.client(
        service_name='s3',
        endpoint_url = endpoint_url
    )


def save_df(s3_client, df, bucket_name: str, file_path: str) -> None:
    full_path = '%s.parquet.gzip' % file_path
    print('Saving dataframe now (%s)' % full_path)

    _buf = BytesIO()
    df.to_parquet(_buf, index=False)
    _buf.seek(0)
    s3_client.put_object(Bucket=bucket_name, Body=_buf.getvalue(), Key=full_path)


def map(
        query,
        db_engine,
        s3_client,
        bucket_name,
        from_date: datetime,
        to_date: datetime = None
):
    end = to_date
    if to_date is None:
        end = datetime.date.today()

    while from_date < end:
        nextday = from_date + timedelta(days = 1)
        df = new_df(query, from_date, nextday, db_engine)
        from_date = nextday
        save_df(s3_client, df, bucket_name, '%s/%s/%s' % (query.db_name, query.table_name, nextday))


class DateParser:
    def create_time_probe(self, from_date: datetime, to_date: datetime) -> str:
        raise NotImplemented

    def parse_time_probe(self, datestr: str) -> [datetime, datetime]:
        raise NotImplementedError

    def get_pattern(self) -> str:
        raise NotImplementedError


class UnderscoredDateParser(DateParser):
    def create_time_probe(self, from_date: datetime, to_date: datetime) -> str:
        return from_date.strftime("%Y-%m-%d") + '_' + to_date.strftime("%Y-%m-%d")

    def parse_time_probe(self, datestr: str) -> [datetime, datetime]:
        from_date, to_date = datestr.split('_')

        return datetime.strptime(from_date, '%Y-%m-%d').date(), datetime.strptime(to_date, '%Y-%m-%d').date()

    def get_pattern(self) -> str:
        return '\b(\d{4})-(\d{2})-(\d{2})_(\d{4})-(\d{2})-(\d{2})\b'


class S3FileMapper:
    def __init__(self, client: s3client, bucket: str):
        self.client = client
        self.bucket = bucket

    def read(self, file_path: str, **args) -> pd.DataFrame:
        df = pd.DataFrame
        for key in self.client.list_objects(Bucket=self.bucket, Prefix=file_path)['Contents']:
            obj = self.client.get_object(Bucket=self.bucket, Key=key['Key'])
            if key['Key'].endswith('.parquet.gzip'):
                df = pd.read_parquet(BytesIO(obj['Body'].read()), **args)
            else:
                df = pd.read_csv(BytesIO(obj['Body'].read()), **args)

        return df

    def save_as_csv(self, df: pd.DataFrame, full_path: str, **args):
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, **args)
        self.client.put_object(Bucket=self.bucket, Body=csv_buffer.getvalue(), Key=full_path)


    def save_as_parquet(self, df: pd.DataFrame, full_path: str, **args):
        _buf = BytesIO()
        df.to_parquet(_buf, *args)
        _buf.seek(0)
        self.client.put_object(Bucket=self.bucket, Body=_buf.getvalue(), Key=full_path)


def create_default_s3mapper(application: Application, bucket: str) -> S3FileMapper:
    s3_client = get_default_s3_client(application)
    return S3FileMapper(s3_client, bucket)


@dataclass
class Semesters:
    fall: str = 'fall'
    spring: str = 'string'

    def get_fall_begin(self, year: int) -> datetime:
        return datetime.date(year, 7, 2)

    def get_fall_end(self, year: int) -> datetime:
        return datetime.date(year, 12, 31)

    def get_spring_begin(self, year: int) -> datetime:
        return datetime.date(year, 1, 1)

    def get_spring_end(self, year: int) -> datetime:
        return datetime.date(year, 7, 1)


class SemesterMapper:
    def __init__(self, mapper: S3FileMapper, date_parser: DateParser, file_path_prefix: str):
        self.mapper = mapper
        self.date_parser = date_parser
        self.file_path_prefix = file_path_prefix

    def exists(self, from_date: datetime, to_date: datetime, **args) -> bool:
        try:
            time_probe = self.date_parser.create_time_probe(from_date, to_date)
            file_path = self.file_path_prefix + '/by_semester/%s.csv' % (time_probe)
            df = self.mapper.read(file_path, **args)
            return True
        except (KeyError):
            return False

    def get(self, from_date: datetime, to_date: datetime, **args) -> pd.DataFrame:
        time_probe = self.date_parser.create_time_probe(from_date, to_date)
        file_path = self.file_path_prefix + '/by_semester/%s.csv' % (time_probe)
        return self.mapper.read(file_path, **args)

    def get_for_semester(self, semester: str, year: int) -> pd.DataFrame:
        if semester == Semesters.fall:
            data_df = self.get(Semesters().get_fall_begin(year), Semesters().get_fall_end(year))

        elif semester == Semesters.spring:
            data_df = self.get(Semesters().get_spring_begin(year), Semesters().get_spring_end(year))

        else:
            raise NotImplementedError(
                "The requested semester must be either %s or %s" % (Semesters.fall, Semesters.spring)
            )

        return data_df

    def save(self, df: pd.DataFrame, semester: str, year: int, **args) -> None:
        if semester == 'fall':
            from_date = Semesters().get_fall_begin(year)
            to_date = Semesters().get_fall_end(year)

        elif semester == Semesters.spring:
            from_date = Semesters().get_spring_begin(year)
            to_date = Semesters().get_spring_end(year)

        else:
            raise NotImplementedError(
                "The requested semester must be either %s or %s" % (Semesters.fall, Semesters.spring)
            )

        time_probe = self.date_parser.create_time_probe(from_date, to_date)
        file_path = self.file_path_prefix + '/by_semester/%s.csv' % (time_probe)

        self.mapper.save_as_csv(df, file_path, **args)


class DateDifference:
    def __init__(
            self,
            df: pd.DataFrame,
            id_col_name: str,
            datetime_col_name: str,
            difference_col_name: str = 'difference(seconds)'
    ):
        self.id_col_name = id_col_name
        self.datetime_col_name = datetime_col_name
        self.difference_col_name = difference_col_name
        self.calculate_for(df)


    def calculate_for(self, df: pd.DataFrame):
        df[self.datetime_col_name] = pd.to_datetime(df[self.datetime_col_name])
        df = df.sort_values(self.datetime_col_name).groupby(self.id_col_name)[self.datetime_col_name].agg(['first','last'])

        df[self.difference_col_name] = (df['last'] - df['first']) / pd.Timedelta(seconds=1)
        self.df = df.reset_index()


    def get_users_with_sessions_between_days(self, min_limit_days: int, max_limit_days: int) -> pd.DataFrame:
        df_max = self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * max_limit_days)
        df_min = self.get_users_with_sessions_more_than(self.num_seconds_in_24_hrs() * min_limit_days)

        return pd.merge(df_max, df_min, how='inner', on=[self.id_col_name])


    def get_users_with_sessions_less_than(self, seconds:int) -> pd.DataFrame:
        return self.df.loc[self.df[self.difference_col_name] <= seconds]


    def get_users_with_sessions_more_than(self, seconds:int) -> pd.DataFrame:
        return self.df.loc[self.df[self.difference_col_name] > seconds]


    def get_24_hour_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs())


    def get_7_day_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * 7)


    def get_30_day_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * 30)


    def get_90_day_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * 90)


    def get_180_day_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * 180)


    def get_365_day_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_less_than(self.num_seconds_in_24_hrs() * 365)


    def get_more_than_1_year_users(self) -> pd.DataFrame:
        return self.get_users_with_sessions_more_than(self.num_seconds_in_24_hrs() * 365)


    def num_seconds_in_24_hrs(self) -> int:
        return 86400


def new_session_lifetime_calculator(application) -> DateDifference:
    df = read_all(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_raw,
        DataLakeConfiguration().toolstart_path,
        logging.getLogger('session_calculation')
    )
    df['datetime'] = pd.to_datetime(df['datetime'])
    return DateDifference(df, 'user', 'datetime')


def num_seconds_in_24_hrs() -> int:
    return 86400


def get_users_with_sessions_less_than(df, seconds:int):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_users_with_sessions_less_than(seconds)


def get_users_with_sessions_more_than(df, seconds:int):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_users_with_sessions_more_than(seconds)


def get_24_hour_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_24_hour_users()


def get_7_day_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_7_day_users()


def get_30_day_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_30_day_users()


def get_90_day_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_90_day_users()


def get_180_day_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_180_day_users()


def get_365_day_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_365_day_users()


def get_more_than_1_year_users(df):
    date_diff = new_session_lifetime_calculator(df)
    return date_diff.get_more_than_1_year_users()


