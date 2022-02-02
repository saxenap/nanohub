from nanoHUB.dataaccess.lake import S3FileMapper, DateParser, UnderscoredDateParser, get_default_s3_client
from nanoHUB.application import Application
from nanoHUB.clustering.overlap import ClustersRepository, MikeXufengOverlap
import datetime
import pandas as pd


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


def get_users_by_semester(db, year, sem: str) -> [int, int] :
    query = "SELECT COUNT(username) AS total FROM nanohub.jos_users WHERE (registerDate BETWEEN '%s' AND '%s');"
    if sem == 'fall':
        query1 = query % (datetime.date(2000, 1, 1), datetime.date(year, 12, 31))
        query2 = query % (datetime.date(year, 7, 2), datetime.date(year, 12, 31))

    else:
        query1 = query % (datetime.date(2000, 1, 1), datetime.date(year, 7, 1))
        query2 = query % (datetime.date(year, 1, 1), datetime.date(year, 7, 1))

    df1 = pd.read_sql_query(query1, db)
    df2 = pd.read_sql_query(query2, db)

    return df1['total'].iloc[0], df2['total'].iloc[0]

def get_cluster_numbers_by_semester(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    db = application.new_db_engine('nanohub')
    data = []
    for year in range(2008, 2022):
        for sem in ['spring', 'fall']:
            df = get_overlap_by_semester(repo, year, sem)
            m_only_cluster_size = int(df['MOnlySize'].sum())
            x_only_cluster_size = int(df['XOnlySize'].sum())
            overlap_size = int(df['OverlapSize'].sum())

            num_registered_users, num_new_registered_users = get_users_by_semester(db, year, sem)
            unregistered_total = num_registered_users - (m_only_cluster_size + x_only_cluster_size + overlap_size)
            data.append([
                year,
                sem,
                num_registered_users,
                num_new_registered_users,
                unregistered_total,
                m_only_cluster_size,
                x_only_cluster_size,
                overlap_size
            ])

    return pd.DataFrame(
        data, columns=['year', 'sem', 'number of all registered users', 'number of newly registered users this semester', 'not_clustered', 'mike_only', 'xufeng_only', 'overlap_mike_xufeng']
    )



