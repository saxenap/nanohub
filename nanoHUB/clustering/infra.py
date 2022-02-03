from nanoHUB.dataaccess.lake import S3FileMapper, create_default_s3mapper, DateParser, UnderscoredDateParser, get_default_s3_client
from nanoHUB.application import Application
from nanoHUB.clustering.overlap import ClustersRepository, MikeXufengOverlap
import datetime
from dateutil.relativedelta import *
import pandas as pd
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from ast import literal_eval



class ClustersBySemester(ClustersRepository):
    def __init__(self, mapper: S3FileMapper, date_parser: DateParser):
        self.mapper = mapper
        self.date_parser = date_parser

    def get(self, alg_name: str, from_date: datetime, to_date: datetime, **args) -> pd.DataFrame:
        time_probe = self.date_parser.create_time_probe(from_date, to_date)
        file_path = 'clusters/%s/by_semester/%s.csv' % (alg_name, time_probe)
        return self.mapper.read(file_path, **args)

    def save(self, df: pd.DataFrame, alg_name: str, from_date: datetime, to_date: datetime, **args) -> None:
        time_probe = self.date_parser.create_time_probe(from_date, to_date)
        file_path = 'clusters/%s/by_semester/%s.csv' % (alg_name, time_probe)

        self.mapper.save_as_csv(df, file_path, **args)


def create_clusters_repository(application: Application, bucket: str) -> ClustersBySemester:
    s3_reader = S3FileMapper(get_default_s3_client(application), bucket)
    return ClustersBySemester(s3_reader, UnderscoredDateParser())


def create_mike_xufeng_overlap_repo(application: Application, bucket: str) -> MikeXufengOverlap:
    clusters = create_clusters_repository(application, bucket)
    return MikeXufengOverlap(clusters)


def get_overlap_by_semester(repo: MikeXufengOverlap, year: int, sem: str) -> pd.DataFrame:
    if sem == 'fall':
        data = repo.get_for(datetime.date(year, 7, 2), datetime.date(year, 12, 31))

    else:
        data = repo.get_for(datetime.date(year, 1, 1), datetime.date(year, 7, 1))

    return data



def db_query_active_users_by_date(db, from_date: datetime, to_date: datetime) -> int :
    query = '''
    SELECT COUNT(DISTINCT starts.user) AS number_active_users
        FROM nanohub_metrics.toolstart AS starts
        WHERE (datetime BETWEEN '%s' AND '%s')
    ;
    '''
    query = query % (from_date, to_date)
    df2 = pd.read_sql_query(query, db)
    return df2['number_active_users'].iloc[0]


def db_query_active_users_by_month(db, year, month: int) -> int :
    first_date = datetime.date(year, month, 1)
    last_date = first_date + relativedelta(months=+1)
    return db_query_active_users_by_date(
        db, first_date, last_date
    )


def db_query_active_users_by_semester(db, year, sem: str) -> int :
    if sem == 'fall':
        result = db_query_active_users_by_date(
            db, datetime.date(year, 7, 2), datetime.date(year, 12, 31)
        )

    else:
        result = db_query_active_users_by_date(
            db, datetime.date(year, 1, 1), datetime.date(year, 7, 1)
        )

    return result


def save_active_users_by_month(application: Application) -> None:
    file_path = 'active_users_by_month.csv'

    mapper = S3FileMapper(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_processed
    )

    db = application.new_db_engine('nanohub_metrics')
    data = []
    for year in range(2008, 2022):
        for month in range(1, 13):
            data.append([year, month, db_query_active_users_by_month(db, year, month)])

    df = pd.DataFrame(data, columns=['year', 'month', 'number_active_users'])
    mapper.save_as_csv(df, file_path, index=None)


def save_active_users_by_semester(application: Application) -> None:
    file_path = 'active_users_by_semester.csv'

    mapper = S3FileMapper(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_processed
    )

    db = application.new_db_engine('nanohub_metrics')
    data = []
    for year in range(2008, 2022):
        for sem in ['fall', 'spring']:
            data.append([year, sem, db_query_active_users_by_semester(db, year, sem)])

    df = pd.DataFrame(data, columns=['year', 'semester', 'number_active_users'])
    mapper.save_as_csv(df, file_path, index=None)


def get_active_users_by_semester(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_users_by_semester.csv'
    return mapper.read(file_path)


def get_active_users_by_month(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_users_by_month.csv'
    return mapper.read(file_path)


def get_cluster_numbers_by_semester(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    data = []
    num_active_users = get_active_users_by_semester(create_default_s3mapper(application, bucket))
    for year in range(2008, 2022):
        for sem in ['spring', 'fall']:
            df = get_overlap_by_semester(repo, year, sem)
            m_only_cluster_size = len(set(df['MOnlyMembers'].apply(literal_eval).sum()))
            x_only_cluster_size = len(set(df['XOnlyMembers'].apply(literal_eval).sum()))
            overlap_size = len(set(df['OverlapMembers'].apply(literal_eval).sum()))
            combined_size = len(set(df['CombinedMembers'].apply(literal_eval).sum()))
            m_combined = m_only_cluster_size + overlap_size
            x_combined = x_only_cluster_size + overlap_size

            num_unique_clustered_users = combined_size
            # print(len(df['CombinedMembers'].apply(literal_eval).sum()), len(set(df['CombinedMembers'].apply(literal_eval).sum())))

            num_active_users_sem = (
                num_active_users.loc[(num_active_users['year'] == year)
                                     & (num_active_users['semester'] == sem),
                'number_active_users'].values[0]
            )
            num_unclustered_active_users_sem = num_active_users_sem - num_unique_clustered_users

            data.append([
                year,
                sem,
                num_active_users_sem,
                num_unclustered_active_users_sem,
                m_only_cluster_size,
                x_only_cluster_size,
                overlap_size,
                m_combined,
                x_combined
            ])

    return pd.DataFrame(
        data, columns=[
            'year',
            'semester',
            'num_active_users',
            'num_unclustered_active_users',
            'mike_only',
            'xufeng_only',
            'overlap_mike_xufeng',
            'total_mike_combined',
            'total_xufeng_combined'
        ]
    )