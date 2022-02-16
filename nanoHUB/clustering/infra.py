from nanoHUB.dataaccess.lake import S3FileMapper, create_default_s3mapper, DateParser, UnderscoredDateParser, get_default_s3_client
from nanoHUB.application import Application
from nanoHUB.clustering.overlap import ClustersRepository, MikeXufengOverlap
import datetime
from dateutil.relativedelta import *
import pandas as pd
import numpy as np
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from ast import literal_eval
from dataclasses import dataclass


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
            AND success=1
            AND user != 'gridstat'
    ;
    '''
    query = query % (from_date, to_date)
    df2 = pd.read_sql_query(query, db)
    return df2['number_active_users'].iloc[0]


def db_query_active_user_ids_by_date(db, from_date: datetime, to_date: datetime) -> pd.DataFrame:
    query = '''
    SELECT DISTINCT starts.user AS active_users
        FROM nanohub_metrics.toolstart AS starts
        WHERE (datetime BETWEEN '%s' AND '%s')
            AND success=1
            AND user != 'gridstat'
    ;
    '''
    query = query % (from_date, to_date)
    df2 = pd.read_sql_query(query, db)
    return df2['active_users']


def db_query_active_users_by_year(db, year: int) -> int :
    first_date = datetime.date(year, 1, 1)
    last_date = datetime.date(year, 12, 31)
    return db_query_active_users_by_date(
        db, first_date, last_date
    )


def db_query_active_users_by_academic_year(db, year: int) -> int :
    first_date = datetime.date(year, 7, 2)
    last_date = datetime.date(year + 1, 7, 1)
    return db_query_active_users_by_date(
        db, first_date, last_date
    )


def db_query_active_user_ids_by_month(db, year, month: int) -> pd.DataFrame :
    first_date = datetime.date(year, month, 1)
    last_date = first_date + relativedelta(months=+1)
    return db_query_active_user_ids_by_date(
        db, first_date, last_date
    )

def db_query_active_users_by_month(db, year, month: int) -> int :
    first_date = datetime.date(year, month, 1)
    last_date = first_date + relativedelta(months=+1)
    return db_query_active_users_by_date(
        db, first_date, last_date
    )


def db_query_active_users_by_semester(db, year, sem: str) -> int :
    if sem.lower() == 'fall':
        result = db_query_active_users_by_date(
            db, datetime.date(year, 7, 2), datetime.date(year, 12, 31)
        )

    elif sem.lower() == 'spring':
        result = db_query_active_users_by_date(
            db, datetime.date(year, 1, 1), datetime.date(year, 7, 1)
        )
    else:
        raise RuntimeError(
            "Invalid value '%s' for semester provided. Allowed values are: spring or fall" % sem
        )

    return result


def save_active_user_ids_by_month(application: Application) -> None:
    file_path = 'active_user_ids_by_month/%d/%d/.csv'

    mapper = S3FileMapper(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_processed
    )

    db = application.new_db_engine('nanohub_metrics')

    for year in range(2008, 2022):
        print(year)
        for month in range(1, 13):
            print(month)
            user_ids = db_query_active_user_ids_by_month(db, year, month)
            mapper.save_as_csv(user_ids, file_path % (year, month), index=None)


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


def save_active_users_by_academic_year(application: Application) -> None:
    file_path = 'number_active_users_by_academic_year.csv'

    mapper = S3FileMapper(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_processed
    )

    db = application.new_db_engine('nanohub_metrics')
    data = []
    for year in range(2008, 2022):
        print(year)
        data.append([year, db_query_active_users_by_academic_year(db, year)])

    df = pd.DataFrame(data, columns=['year', 'number_active_users'])
    mapper.save_as_csv(df, file_path, index=None)


def save_active_users_by_year(application: Application) -> None:
    file_path = 'active_users_by_year.csv'

    mapper = S3FileMapper(
        get_default_s3_client(application),
        ClusteringConfiguration().bucket_name_processed
    )

    db = application.new_db_engine('nanohub_metrics')
    data = []
    for year in range(2008, 2022):
        print(year)
        data.append([year, db_query_active_users_by_year(db, year)])

    df = pd.DataFrame(data, columns=['year', 'number_active_users'])
    mapper.save_as_csv(df, file_path, index=None)


def get_active_users_by_semester(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_users_by_semester.csv'
    return mapper.read(file_path)


def get_active_users_by_academic_year(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'number_active_users_by_academic_year.csv'
    return mapper.read(file_path)


def get_active_users_by_year(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_users_by_year.csv'
    return mapper.read(file_path)


def get_active_users_by_month(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_users_by_month.csv'
    return mapper.read(file_path)

def get_active_user_ids_by_month(mapper: S3FileMapper) -> pd.DataFrame:
    file_path = 'active_user_ids_by_month/%d/%d/.csv'
    final_df = pd.DataFrame(columns=['year', 'month', 'active_users'])
    rows_list = []
    for year in range(2008, 2022):
        for month in range(1, 13):
            user_ids_dict = {}
            user_ids_dict['year'] = year
            user_ids_dict['month'] = month
            df = mapper.read(file_path % (year, month))
            user_ids_dict['active_users'] = df['active_users']
            final_df.append([year])
            rows_list.append(user_ids_dict)

    return pd.DataFrame(rows_list, columns=['year', 'month', 'active_users'])


def get_active_user_ids_by_semester(mapper: S3FileMapper) -> int :
    file_path = 'active_user_ids_by_month/%d/%d/.csv'
    for year in range(2008, 2022):
        for month in range(1, 13):
            df = mapper.read(file_path % (year, month))
            print(df)
            raise


    return result


def add_cluster_info(all_users: pd.DataFrame, cluster_repo: ClustersBySemester) -> pd.DataFrame:
    all_users['clusters'] = np.empty((len(all_users), 0)).tolist()

    for year in range(2008, 2022):
        for sem in ['fall', 'spring']:
            for alg in ['mike', 'xufeng']:
                try:
                    cluster_name = alg + '_' + sem + '_' + str(year)
                    if sem == 'fall':
                        if alg == 'xufeng':
                            df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31),header=None)
                        else:
                            df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31))

                    else:
                        if alg == 'xufeng':
                            df = cluster_repo.get(alg, datetime.date(year + 1, 1, 1), datetime.date(year + 1, 7, 1),header=None)
                        else:
                            df = cluster_repo.get(alg, datetime.date(year + 1, 1, 1), datetime.date(year + 1, 7, 1))

                    result_set = set()
                    for column in df.columns:
                        result_set = result_set.union(df[column].values)

                    condition = all_users["username"].isin(list(result_set))
                    all_users["clusters"] = np.where(condition, all_users['clusters'].apply(lambda x: x + [cluster_name]), all_users['clusters'])
                    all_users[cluster_name] = np.where(condition, True, False)
                    all_users["is_researcher"] = np.where(condition, True, all_users['is_researcher'])
                except KeyError:
                    pass
    return all_users




def get_cluster_numbers_by_semester(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    data = []
    num_active_users = get_active_users_by_semester(create_default_s3mapper(application, bucket))
    k = 0
    previous_sem = {}
    previous_sem_members = []
    previous_sem_clustered_users = set()
    data_previous_sems = []
    for year in range(2008, 2022):
        for sem in ['spring', 'fall']:
            if year == 2008 and sem == 'spring':
                continue
            df = get_overlap_by_semester(repo, year, sem)
            m_only_members = set(df['MOnlyMembers'].apply(literal_eval).sum())
            m_only_cluster_size = len(m_only_members)
            x_only_members = set(df['XOnlyMembers'].apply(literal_eval).sum())
            x_only_cluster_size = len(x_only_members)
            overlap_members = set(df['OverlapMembers'].apply(literal_eval).sum())
            # overlap_size = len(overlap_members)

            overlap_members = overlap_members.union(m_only_members.intersection(x_only_members))
            overlap_size = len(overlap_members)

            combined_size = len(set(df['CombinedMembers'].apply(literal_eval).sum()))
            m_combined = m_only_cluster_size + overlap_size
            x_combined = x_only_cluster_size + overlap_size

            # num_unique_clustered_users = combined_size
            # print(len(df['CombinedMembers'].apply(literal_eval).sum()), len(set(df['CombinedMembers'].apply(literal_eval).sum())))

            num_active_users_sem = (
                num_active_users.loc[(num_active_users['year'] == year)
                                     & (num_active_users['semester'] == sem),
                'number_active_users'].values[0]
            )
            # num_unique_clustered_users = m_only_cluster_size + x_only_cluster_size + overlap_size
            # num_unique_clustered_users1 = num_unique_clustered_users
            # num_unclustered_active_users_sem = num_active_users_sem - num_unique_clustered_users

            unique_members = m_only_members.union(x_only_members, overlap_members)
            num_unique_clustered_users = len(unique_members)
            num_unclustered_active_users_sem = num_active_users_sem - num_unique_clustered_users

            new_clustered_users_current_sem = unique_members.difference(previous_sem_clustered_users)
            previous_sem_clustered_users = new_clustered_users_current_sem
            num_new_clustered_users_current_sem = len(new_clustered_users_current_sem)


            data_point = {}
            data_point['num_active_users'] = num_active_users_sem
            data_point['num_new_clustered_users_current_sem'] = num_new_clustered_users_current_sem
            data_point['num_unclustered_active_users'] = num_unclustered_active_users_sem
            data_point['num_unique_clustered_users'] = num_unique_clustered_users
            data_point['num_users_m_only'] = m_only_cluster_size
            data_point['num_users_x_only'] = x_only_cluster_size
            data_point['num_users_overlap_mike_xufeng'] = overlap_size
            data_point['combined_size'] = combined_size
            data_point['m_combined'] = m_combined
            data_point['x_combined'] = x_combined

            data_previous_sems.append(data_point)
            data_previous_sems = data_previous_sems[-3:]

            dd = {}
            dd['year'] = year
            dd['semester'] = sem

            for key in data_point:
                dd[key] = data_point[key]
                dd['trailing_' + key] = sum(
                    d[key] for d in data_previous_sems
                ) / len(data_previous_sems)


            # dd.update(data_point)
            data.append(dd)

    return pd.DataFrame(data)


def get_stacked_members_by_academic_year(cluster_repo: ClustersBySemester, alg: str, year: int) -> set:
    if alg == 'xufeng':
        df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31),header=None)
    else:
        df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31))

    result_set = set()

    for column in df.columns:
        result_set = result_set.union(df[column].values)

    try:
        if alg == 'xufeng':
            df_spring = cluster_repo.get(alg, datetime.date(year + 1, 1, 1), datetime.date(year + 1, 7, 1),header=None)
        else:
            df_spring = cluster_repo.get(alg, datetime.date(year + 1, 1, 1), datetime.date(year + 1, 7, 1))
        for column in df.columns:
            spring_result = df_spring[column].values
            result_set = result_set.union(spring_result)

    except KeyError:
        pass

    return result_set

def get_stacked_members_by_year(cluster_repo: ClustersBySemester, alg: str, year: int, academic_year: bool = False) -> set:
    spring_year = year
    if academic_year:
        spring_year = year + 1
    if alg == 'xufeng':
        df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31),header=None)
    else:
        df = cluster_repo.get(alg, datetime.date(year, 7, 2), datetime.date(year, 12, 31))

    result_set = set()

    for column in df.columns:
        result_set = result_set.union(df[column].values)

    try:
        if alg == 'xufeng':
            df_spring = cluster_repo.get(alg, datetime.date(spring_year, 1, 1), datetime.date(spring_year, 7, 1),header=None)
        else:
            df_spring = cluster_repo.get(alg, datetime.date(spring_year, 1, 1), datetime.date(spring_year, 7, 1))
        for column in df.columns:
            spring_result = df_spring[column].values
            result_set = result_set.union(spring_result)

    except KeyError:
        pass

    return result_set

def get_cluster_numbers_by_year_ver2(application: Application, bucket: str) -> pd.DataFrame:
    cluster_repo = create_clusters_repository(application, bucket)
    data = []
    active_users_by_year = get_active_users_by_year(create_default_s3mapper(application, bucket))
    active_users_by_academic_year = get_active_users_by_academic_year(create_default_s3mapper(application, bucket))

    for year in range(2008, 2022):
        data_point = {}
        data_point['Date'] = datetime.date(year+1, 7, 2)

        num_active_users_year = (
            active_users_by_academic_year.loc[
                (active_users_by_academic_year['year'] == year), 'number_active_users'
            ].values[0]
        )

        data_point['active_users'] = num_active_users_year

        mike_set = get_stacked_members_by_year(cluster_repo, 'mike', year, academic_year=True)
        xufeng_set = get_stacked_members_by_year(cluster_repo, 'xufeng', year, academic_year=True)

        data_point['num_users_m_only'] = len(mike_set.difference(xufeng_set))

        data_point['num_users_x_only'] = len(xufeng_set.difference(mike_set))

        overlap_set = mike_set.intersection(xufeng_set)
        data_point['num_users_overlap_mike_xufeng'] = len(overlap_set)

        data_point['num_unclustered_active_users'] = num_active_users_year - (
            data_point['num_users_m_only'] + data_point['num_users_x_only'] + data_point['num_users_overlap_mike_xufeng']
        )

        data.append(data_point)

        data_point = {}
        data_point['Date'] = datetime.date(year+1, 1, 1)

        num_active_users_year = (
            active_users_by_year.loc[(active_users_by_year['year'] == year), 'number_active_users'].values[0]
        )

        data_point['active_users'] = num_active_users_year

        mike_set = get_stacked_members_by_year(cluster_repo, 'mike', year)
        xufeng_set = get_stacked_members_by_year(cluster_repo, 'xufeng', year)

        data_point['num_users_m_only'] = len(mike_set.difference(xufeng_set))

        data_point['num_users_x_only'] = len(xufeng_set.difference(mike_set))

        overlap_set = mike_set.intersection(xufeng_set)
        data_point['num_users_overlap_mike_xufeng'] = len(overlap_set)

        data_point['num_unclustered_active_users'] = num_active_users_year - (
                data_point['num_users_m_only'] + data_point['num_users_x_only'] + data_point['num_users_overlap_mike_xufeng']
        )

        data.append(data_point)

    return pd.DataFrame(data)



def get_cluster_numbers_by_year_ver1(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    data = []
    num_active_users = get_active_users_by_semester(create_default_s3mapper(application, bucket))
    previous_sem_clustered_users = set()
    data_previous_sems = []

    for year in range(2008, 2022):

        df_fall = get_overlap_by_semester(repo, year, 'fall')
        try:
            df_spring = get_overlap_by_semester(repo, year + 1, 'spring')
        except KeyError:
            df_spring = pd.DataFrame

        m_only_members = set(df_fall['MOnlyMembers'].apply(literal_eval).sum())
        x_only_members = set(df_fall['XOnlyMembers'].apply(literal_eval).sum())
        overlap_members = set(df_fall['OverlapMembers'].apply(literal_eval).sum())

        num_active_users_year = (
            num_active_users.loc[(num_active_users['year'] == year)
                                 & (num_active_users['semester'] == 'fall'),
                                 'number_active_users'].values[0]
        )

        if not df_spring.empty:
            m_only_members = m_only_members.union(
                set(df_spring['MOnlyMembers'].apply(literal_eval).sum())
            )
            x_only_members = x_only_members.union(
                set(df_spring['XOnlyMembers'].apply(literal_eval).sum())
            )
            overlap_members = overlap_members.union(
                set(df_spring['OverlapMembers'].apply(literal_eval).sum())
            )

            num_active_users_year = num_active_users_year + (
                num_active_users.loc[(num_active_users['year'] == year + 1)
                                     & (num_active_users['semester'] == 'spring'),
                                     'number_active_users'].values[0]
            )

        m_only_cluster_size = len(m_only_members)
        x_only_cluster_size = len(x_only_members)
        overlap_size = len(overlap_members)

        m_combined = m_only_cluster_size + overlap_size
        x_combined = x_only_cluster_size + overlap_size

        unique_members = m_only_members.union(x_only_members, overlap_members)
        num_unique_clustered_users = len(unique_members)
        num_unclustered_active_users_sem = num_active_users_year - num_unique_clustered_users

        list_members = [m_only_members, x_only_members, overlap_members]
        unique_members2 = set().union(*list_members)
        num_unique_clustered_users2 = len(unique_members2)


        new_clustered_users = unique_members.difference(previous_sem_clustered_users)
        previous_sem_clustered_users = new_clustered_users
        num_new_clustered_users = len(new_clustered_users)

        data_point = {}
        data_point['num_active_users'] = num_active_users_year
        # data_point['num_new_clustered_users'] = num_new_clustered_users
        data_point['num_unclustered_active_users'] = num_unclustered_active_users_sem
        data_point['num_unique_clustered_users'] = num_unique_clustered_users
        data_point['num_unique_clustered_users2'] = num_unique_clustered_users2
        data_point['num_users_m_only'] = m_only_cluster_size
        data_point['num_users_x_only'] = x_only_cluster_size
        data_point['num_users_overlap_mike_xufeng'] = overlap_size
        data_point['m_combined'] = m_combined
        data_point['x_combined'] = x_combined

        data_previous_sems.append(data_point)
        data_previous_sems = data_previous_sems[-3:]

        dd = {}
        dd['year'] = year

        for key in data_point:
            dd[key] = data_point[key]
            # dd['trailing_' + key] = sum(
            #     d[key] for d in data_previous_sems
            # ) / len(data_previous_sems)

        # dd.update(data_point)
        data.append(dd)

    return pd.DataFrame(data)


def get_yearly_total_for(df: pd.DataFrame, key: str, year):
    total = df[(df['year'] == year) & (df['semester'] == 'fall')][key].item()
    if ((df['year'] == year + 1) & (df['semester'] == 'spring')).any():
        total = total + df[(df['year'] == year + 1) & (df['semester'] == 'spring')][key].item()
    return total


def get_cluster_numbers_by_year(application: Application, bucket: str) -> pd.DataFrame:
    df_by_sems = get_cluster_numbers_by_semester(application, bucket)
    years = []
    for year in sorted(set(df_by_sems['year'].values)):
        yearly = {}
        yearly['academic_year'] = str(year)
        yearly['num_active_users'] = get_yearly_total_for(df_by_sems, 'num_active_users', year)
        yearly['num_users_m_only'] = get_yearly_total_for(df_by_sems, 'num_users_m_only', year)
        yearly['num_users_x_only'] = get_yearly_total_for(df_by_sems, 'num_users_x_only', year)
        yearly['num_users_overlap_mike_xufeng'] = get_yearly_total_for(df_by_sems, 'num_users_overlap_mike_xufeng', year)
        yearly['num_unclustered_active_users'] = get_yearly_total_for(df_by_sems, 'num_unclustered_active_users', year)
        years.append(yearly)

    return pd.DataFrame(years)



def get_cluster_numbers_by_semester_dups(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    data = []
    num_active_users = get_active_users_by_semester(create_default_s3mapper(application, bucket))
    k = 0
    previous_sem = {}
    previous_sem_members = set()
    average_cals = []
    for year in range(2008, 2022):
        for sem in ['spring', 'fall']:
            if year == 2008 and sem == 'spring':
                continue
            df = get_overlap_by_semester(repo, year, sem)
            m_only_members = set(df['MOnlyMembers'].apply(literal_eval).sum())
            m_only_cluster_size = len(m_only_members)
            x_only_members = set(df['XOnlyMembers'].apply(literal_eval).sum())
            x_only_cluster_size = len(x_only_members)
            overlap_members = set(df['OverlapMembers'].apply(literal_eval).sum())
            overlap_size = len(overlap_members)
            combined_size = len(set(df['CombinedMembers'].apply(literal_eval).sum()))
            m_combined = m_only_cluster_size + overlap_size
            x_combined = x_only_cluster_size + overlap_size

            # num_unique_clustered_users = combined_size

            # print(len(df['CombinedMembers'].apply(literal_eval).sum()), len(set(df['CombinedMembers'].apply(literal_eval).sum())))

            num_active_users_sem = (
                num_active_users.loc[(num_active_users['year'] == year)
                                     & (num_active_users['semester'] == sem),
                                     'number_active_users'].values[0]
            )

            unique_members = m_only_members.union(x_only_members, overlap_members)
            num_unique_clustered_users = len(unique_members)
            num_unclustered_active_users_sem = num_active_users_sem - num_unique_clustered_users

            new_clustered_users_current_sem = unique_members.difference(previous_sem_members)
            num_new_clustered_users_current_sem = len(new_clustered_users_current_sem)

            data_point = {}
            data_point['year'] = year
            data_point['sem'] = sem
            data_point['num_active_users_sem'] = num_active_users_sem
            data_point['num_new_clustered_users_current_sem'] = num_new_clustered_users_current_sem
            data_point['num_unclustered_active_users_sem'] = num_unclustered_active_users_sem
            data_point['num_unique_clustered_users'] = num_unique_clustered_users
            data_point['num_unclustered_active_users_sem'] = num_unclustered_active_users_sem
            data_point['m_only_cluster_size'] = m_only_cluster_size
            data_point['x_only_cluster_size'] = x_only_cluster_size
            data_point['overlap_size'] = overlap_size
            data_point['combined_size'] = combined_size
            data_point['m_combined'] = m_combined
            data_point['x_combined'] = x_combined

            average_cals.append(data_point)

            data_point['avg_num_active_users_sem'] = sum(d['num_active_users_sem'] for d in average_cals) / len(average_cals)
            data_point['avg_num_new_clustered_users_current_sem'] = sum(d['num_new_clustered_users_current_sem'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unclustered_active_users_sem'] = sum(d['num_unclustered_active_users_sem'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unique_clustered_users'] = sum(d['num_unique_clustered_users'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unclustered_active_users_sem'] = sum(d['num_unclustered_active_users_sem'] for d in average_cals) / len(average_cals)

            data_point['avg_m_only_cluster_size'] = sum(d['m_only_cluster_size'] for d in average_cals) / len(average_cals)

            data_point['avg_x_only_cluster_size'] = sum(d['x_only_cluster_size'] for d in average_cals) / len(average_cals)

            data_point['avg_overlap_size'] = sum(d['overlap_size'] for d in average_cals) / len(average_cals)

            data_point['avg_combined_size'] = sum(d['combined_size'] for d in average_cals) / len(average_cals)

            data_point['avg_m_combined'] = sum(d['m_combined'] for d in average_cals) / len(average_cals)

            data_point['avg_x_combined'] = sum(d['x_combined'] for d in average_cals) / len(average_cals)


            if sem == 'spring':
                average_cals = []

            previous_sem = data_point
            previous_sem_members = unique_members
            data.append(data_point.values())

    return pd.DataFrame(
        data, columns=[
            'year',
            'semester',
            'num_active_users',
            'num_new_clustered_users_current_sem',
            'num_unclustered_active_users',
            'num_unique_clustered_users',
            'mike_only',
            'xufeng_only',
            'overlap_mike_xufeng',
            'combined',
            'total_mike_combined',
            'total_xufeng_combined',
            'avg_num_active_users_sem',
            'avg_num_new_clustered_users_current_sem',
            'avg_num_unclustered_active_users',
            'avg_num_clustered_active_users',
            'avg_num_unclustered_active_users',
            'avg_mike_only',
            'avg_xufeng_only',
            'avg_overlap_mike_xufeng',
            'avg_combined',
            'avg_total_mike_combined',
            'avg_total_xufeng_combined'
        ]
    )



def get_dups(application: Application, bucket: str) -> pd.DataFrame:
    repo = create_mike_xufeng_overlap_repo(application, bucket)
    data = []
    num_active_users = get_active_users_by_semester(create_default_s3mapper(application, bucket))
    k = 0
    previous_sem = {}
    previous_sem_members = set()
    average_cals = []
    for year in range(2008, 2022):
        for sem in ['spring', 'fall']:
            if year == 2008 and sem == 'spring':
                continue
            df = get_overlap_by_semester(repo, year, sem)
            m_only_members = set(df['MOnlyMembers'].apply(literal_eval).sum())
            m_only_cluster_size = len(m_only_members)
            x_only_members = set(df['XOnlyMembers'].apply(literal_eval).sum())
            x_only_cluster_size = len(x_only_members)
            overlap_members = set(df['OverlapMembers'].apply(literal_eval).sum())
            overlap_size = len(overlap_members)
            combined_size = len(set(df['CombinedMembers'].apply(literal_eval).sum()))
            m_combined = m_only_cluster_size + overlap_size
            x_combined = x_only_cluster_size + overlap_size

            # num_unique_clustered_users = combined_size

            # print(len(df['CombinedMembers'].apply(literal_eval).sum()), len(set(df['CombinedMembers'].apply(literal_eval).sum())))

            num_active_users_sem = (
                num_active_users.loc[(num_active_users['year'] == year)
                                     & (num_active_users['semester'] == sem),
                                     'number_active_users'].values[0]
            )
            num_unique_clustered_users = m_only_cluster_size + x_only_cluster_size + overlap_size
            num_unique_clustered_users1 = num_unique_clustered_users
            num_unclustered_active_users_sem = num_active_users_sem - num_unique_clustered_users

            print('m_only')
            print(m_only_cluster_size)
            print(m_only_members)
            print('')
            print('')
            print('')
            print('')
            print('')
            print('x_only')
            print(x_only_cluster_size)
            print(x_only_members)
            print('')
            print('')
            print('')
            print('')
            print('')
            print('duplicates')
            print(len(x_only_members & m_only_members))
            print(['duplicates:', x_only_members & m_only_members])
            print('')
            print('')
            print('')
            print('')
            print('')
            print('overlap')
            print(overlap_size)
            print(['overlaps:', overlap_members])
            raise
            test_num_m_only_members = len(m_only_members.union(x_only_members))
            print(['m-only', m_only_cluster_size, test_num_m_only_members])

            test_num_x_only_members = len(x_only_members.union(m_only_members))
            print(['x-only', x_only_cluster_size, test_num_x_only_members])

            print(['duplicates:', overlap_size, len(x_only_members & m_only_members)])

            print('')
            unique_members = m_only_members.union(x_only_members, overlap_members)
            num_unique_clustered_users2 = len(unique_members)
            num_unclustered_active_users_sem2 = num_active_users_sem - num_unique_clustered_users2

            new_clustered_users_current_sem = unique_members.difference(previous_sem_members)
            num_new_clustered_users_current_sem = len(new_clustered_users_current_sem)

            data_point = {}
            data_point['year'] = year
            data_point['sem'] = sem
            data_point['num_active_users_sem'] = num_active_users_sem
            data_point['num_new_clustered_users_current_sem'] = num_new_clustered_users_current_sem
            data_point['num_unclustered_active_users_sem'] = num_unclustered_active_users_sem
            data_point['num_unique_clustered_users1'] = num_unique_clustered_users1
            data_point['num_unique_clustered_users2'] = num_unique_clustered_users2
            data_point['num_unclustered_active_users_sem2'] = num_unclustered_active_users_sem2
            data_point['m_only_cluster_size'] = m_only_cluster_size
            data_point['x_only_cluster_size'] = x_only_cluster_size
            data_point['overlap_size'] = overlap_size
            data_point['combined_size'] = combined_size
            data_point['m_combined'] = m_combined
            data_point['x_combined'] = x_combined

            average_cals.append(data_point)

            data_point['avg_num_active_users_sem'] = sum(d['num_active_users_sem'] for d in average_cals) / len(average_cals)
            data_point['avg_num_new_clustered_users_current_sem'] = sum(d['num_new_clustered_users_current_sem'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unclustered_active_users_sem'] = sum(d['num_unclustered_active_users_sem'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unique_clustered_users1'] = sum(d['num_unique_clustered_users1'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unique_clustered_users2'] = sum(d['num_unique_clustered_users2'] for d in average_cals) / len(average_cals)

            data_point['avg_num_unclustered_active_users_sem2'] = sum(d['num_unclustered_active_users_sem2'] for d in average_cals) / len(average_cals)

            data_point['avg_m_only_cluster_size'] = sum(d['m_only_cluster_size'] for d in average_cals) / len(average_cals)

            data_point['avg_x_only_cluster_size'] = sum(d['x_only_cluster_size'] for d in average_cals) / len(average_cals)

            data_point['avg_overlap_size'] = sum(d['overlap_size'] for d in average_cals) / len(average_cals)

            data_point['avg_combined_size'] = sum(d['combined_size'] for d in average_cals) / len(average_cals)

            data_point['avg_m_combined'] = sum(d['m_combined'] for d in average_cals) / len(average_cals)

            data_point['avg_x_combined'] = sum(d['x_combined'] for d in average_cals) / len(average_cals)


            if sem == 'spring':
                average_cals = []

            previous_sem = data_point
            previous_sem_members = unique_members
            data.append(data_point.values())

    return pd.DataFrame(
        data, columns=[
            'year',
            'semester',
            'num_active_users',
            'num_new_clustered_users_current_sem',
            'num_unclustered_active_users',
            'num_unique_clustered_users1',
            'num_unique_clustered_users2',
            'num_unclustered_active_users2',
            'mike_only',
            'xufeng_only',
            'overlap_mike_xufeng',
            'combined',
            'total_mike_combined',
            'total_xufeng_combined',
            'avg_num_active_users_sem',
            'avg_num_new_clustered_users_current_sem',
            'avg_num_unclustered_active_users',
            'avg_num_clustered_active_users1',
            'avg_num_clustered_active_users2',
            'avg_num_unclustered_active_users2',
            'avg_mike_only',
            'avg_xufeng_only',
            'avg_overlap_mike_xufeng',
            'avg_combined',
            'avg_total_mike_combined',
            'avg_total_xufeng_combined'
        ]
    )

