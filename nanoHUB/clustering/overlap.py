import pandas as pd
import datetime


def get_set_from(df: pd.DataFrame):
    return df.apply(frozenset, axis=1)


def get_cluster_overlap(df_m: pd.DataFrame, df_x: pd.DataFrame) -> pd.DataFrame:

    m_id = 1
    x_id = 1

    series_set_m = get_set_from(df_m)
    series_set_x = get_set_from(df_x)

    # loop over Mike classes and find overlaps with Xufeng classes.   
    # Sort out in each of Mike's classes which ones are overlap members and Xfeng only or Mike only
    # we are NOT doing an exhaustive search over ALL the classes found - just the Mike classes

    overlap_list = []
    for m_line in series_set_m:
        m_set = set(m_line)
        # remove nan values
        m_set = {x for x in m_set if x==x}
        for x_line in series_set_x:
            x_set = set(x_line)
            # remove nan values
            x_set = {x for x in x_set if x==x}
            both = m_set & x_set
            combined = m_set | x_set
            m_only = m_set - x_set
            x_only = x_set - m_set
            if len(both) > 0:
                overlap_list.append(
                    [m_id, x_id, len(m_line), len(x_line), len(both), list(both), len(m_only), list(m_only),
                     len(x_only), list(x_only), len(combined), list(combined)])
            x_id += 1
        x_id = 1
        m_id += 1

    # we need to capture all the classes found by Xufeng, that have NO OVERLAP at all with any of Mike classes. 
    # This is a to do item to be performed. 
    # XXXXX    

    
    overlap_list.sort(key=lambda x: (x[0], -x[3]))
    return pd.DataFrame(overlap_list, columns = [
        'MClusterID', 'XClusterID', 'MClusterSize', 'XClusterSize', 'OverlapSize', 'OverlapMembers', 'MOnlySize',
        'MOnlyMembers', 'XOnlySize', 'XOnlyMembers', 'CombinedSize', 'CombinedMembers'
    ])


def combined_x_clusters(df_m: pd.DataFrame, df_x: pd.DataFrame) -> []:

    m_id = 1
    x_id = 1

    series_set_m = get_set_from(df_m)
    series_set_x = get_set_from(df_x)

    combined_list = []
    for m_line in series_set_m:
        m_set = set(m_line)
        x_set = set()
        for x_line in series_set_x:
            x_set_tmp = set(x_line)
            both = m_set & x_set_tmp
            if len(both) > 0:
                x_set.update(x_set_tmp)
            x_id += 1

        # store result
        combined_list.append((m_set, x_set))
        x_id = 1
        m_id += 1
    return combined_list


class ClustersRepository:
    def get(self, alg_name: str, from_date: datetime, to_date: datetime, **args) -> pd.DataFrame:
        raise NotImplementedError

    def save(self, df: pd.DataFrame, alg_name: str, from_date: datetime, to_date: datetime, **args) -> None:
        raise NotImplementedError


class MikeXufengOverlap:
    def __init__(
            self,
            repo: ClustersRepository,
            overlap_name:str = 'mike-xufeng-overlap',
            mike_name: str = 'mike',
            xufeng_name: str = 'xufeng'
    ):
        self.repo = repo
        self.overlap_name = overlap_name
        self.mike_name = mike_name
        self.xufeng_name = xufeng_name

    def save_for(self, from_date: datetime, to_date: datetime) -> None:
        df_m = self.repo.get(self.mike_name, from_date, to_date)
        df_x = self.repo.get(self.xufeng_name, from_date, to_date, header=None)
        overlap_df = get_cluster_overlap(df_m, df_x)
        self.repo.save(overlap_df, self.overlap_name, from_date, to_date, index=False)

    def get_for(self, from_date: datetime, to_date: datetime) -> pd.DataFrame:
        return self.repo.get(
            self.overlap_name, from_date, to_date
        )
