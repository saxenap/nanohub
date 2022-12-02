import pandas as pd
from dataclasses import dataclass, field
import time, datetime
from io import BytesIO
import boto3
import re
# from nanoHUB.dataaccess.lake import DateParser
import logging

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


@dataclass
class QueryStringForAll:
    db_name: str
    table_name: str
    col_names: []
    datetime_cols: []

    def make_query(self) -> str:
        sql = '''
        SELECT %s FROM %s.%s;
        '''.strip()

        return sql % (
            ','.join(self.col_names),
            self.db_name,
            self.table_name
        )

    def get_datetime_cols(self) -> []:
        return self.datetime_cols

def new_df(query: QueryString, from_date: datetime, to_date: datetime, engine):
    print(query.make_query(from_date, to_date))
    df = pd.read_sql_query(query.make_query(from_date, to_date), engine)

    for col_name in query.datetime_cols:
        df[col_name] = pd.to_datetime(df[col_name],errors='coerce')

    return df


def new_df_for_all(query: QueryStringForAll, engine):
    print(query.make_query())
    df = pd.read_sql_query(query.make_query(), engine)

    for col_name in query.datetime_cols:
        df[col_name] = pd.to_datetime(df[col_name],errors='coerce')

    return df


def get_default_s3_client(application):
    """Creates a new low-level service client for interacting with Geddes

    Args:
        application (nanoHUB.Application): An object of the application class

    Returns
    boto_session.client:  a low-level service client by service.
    """
    return get_s3_client(
        'https://' + application.get_config_value('geddesapi.endpoint') + ':443',
        application.get_config_value('geddesapi.access_key'),
        application.get_config_value('geddesapi.secret_key')
    )


def get_s3_client(endpoint_url: str, access_key: str, secret: str):

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
        bucket_name: str,
        from_date: datetime,
        to_date: datetime = None
):
    end = to_date
    if to_date is None:
        end = datetime.date.today()

    while from_date < end:
        nextday = from_date + datetime.timedelta(days = 1)
        df = new_df(query, from_date, nextday, db_engine)
        from_date = nextday
        save_df(s3_client, df, bucket_name, '%s/%s/%s' % (query.db_name, query.table_name, nextday))


def map_for_all(
        query,
        db_engine,
        s3_client,
        bucket_name: str
):

    df = new_df_for_all(query, db_engine)
    save_df(s3_client, df, bucket_name, '%s/%s' % (query.db_name, query.table_name))

# def read(
#         s3_client,
#         bucket_name: str,
#         from_date: datetime = None,
#         to_date: datetime = None
# ):
#     end = to_date
#     if to_date is None:
#         end = datetime.date.today()
#
#     while from_date < end:
#         nextday = from_date + datetime.timedelta(days = 1)
#         df = read_


def read_all(
        s3_client,
        bucket_name: str,
        table_name: str,
        logger: logging.Logger,
        **args
):
    li = []
    for key in s3_client.list_objects(Bucket=bucket_name, Prefix=table_name)['Contents']:
        logger.debug('Reading: ' + key['Key'])
        obj = s3_client.get_object(Bucket=bucket_name, Key=key['Key'])
        if key['Key'].endswith('.parquet.gzip'):
            df = pd.read_parquet(BytesIO(obj['Body'].read()), **args)
        else:
            df = pd.read_csv(BytesIO(obj['Body'].read()), **args)
        li.append(df)

    return pd.concat(li, axis=0, ignore_index=True)


# def has_any_file(
#         s3_client,
#         bucket_name: str,
#         table_name: str,
# ):
#     for key in s3_client.list_objects(Bucket=bucket_name, Prefix=table_name)['Contents']:
#         return True
#
# def get_latest_file(
#         s3_client,
#         bucket_name: str,
#         table_name: str,
#         date_parser: DateParser
# ):
#     filenames = get_all_files_in(
#         s3_client, bucket_name, table_name
#     )
#     dates = (get_date(date_parser, fn) for fn in filenames)
#     dates = (d for d in dates if d is not None)
#     last_date = max(dates)
#     last_date = last_date.strftime('%m-%d-%Y')
#     filenames = [fn for fn in filenames if last_date in fn]
#     for fn in filenames:
#         print(fn)
#
# def get_all_files_in(
#         s3_client,
#         bucket_name: str,
#         table_name: str,
# ) -> []:
#     keys = []
#     for key in s3_client.list_objects(Bucket=bucket_name, Prefix=table_name)['Contents']:
#         keys.append(key['Key'])
#
#     return keys
#
# def get_date(date_parser: DateParser, filename: str) -> datetime:
#     date_pattern = re.compile(date_parser.get_pattern())
#     matched = date_pattern.search(filename)
#     if not matched:
#         return None
#     m, d, y = map(int, matched.groups())
#     return datetime.date(y, m, d)


