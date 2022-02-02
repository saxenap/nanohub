import pandas as pd
from dataclasses import dataclass, field
from datetime import datetime, timedelta, date
from io import BytesIO, StringIO
import boto3
import os
import botocore.client as s3client


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
        end = date.today()

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


class UnderscoredDateParser(DateParser):
    def create_time_probe(self, from_date: datetime, to_date: datetime) -> str:
        return from_date.strftime("%Y-%m-%d") + '_' + to_date.strftime("%Y-%m-%d")

    def parse_time_probe(self, datestr: str) -> [datetime, datetime]:
        from_date, to_date = datestr.split('_')

        return datetime.strptime(from_date, '%Y-%m-%d').date(), datetime.strptime(to_date, '%Y-%m-%d').date()


class S3FileMapper:
    def __init__(self, client: s3client, bucket: str):
        self.client = client
        self.bucket = bucket

    def read(self, file_path: str, **args) -> pd.DataFrame:
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

