import pandas as pd
from dataclasses import dataclass, field
import time, datetime
from io import BytesIO
import boto3
from nanoHUB.application import Application

@dataclass
class QueryString:
    db_name: str
    table_name: str
    from_col_name: str
    to_col_name: str
    col_names: [] = field(default_factory=lambda: ['*'])
    datetime_cols = []

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


def get_default_s3_client():
    application = Application.get_instance()
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
        bucket_name,
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


