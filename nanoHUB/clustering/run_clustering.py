import os
from dataclasses import dataclass, field
from datetime import datetime, date
import pandas as pd
import logging
from nanoHUB.clustering.algorithms_map import (
    DateValidator, AlgorithmsMap, AlgorithmHandler, GeddesSaver, DisplayDf, DataframeLogger, ValidationHandler, LocalDriveSaver
)
from dateutil.relativedelta import relativedelta


@dataclass
class ExecuteAlgorithmCommand:
    #general
    task: str
    start_date: str #datetimeformat: ####-##-##
    end_date: str #datetimeformat: ####-##-##

    #data
    geoip2_mmdb_filepath: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb')) #check

    #directories
    output_dir: str = field(default = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')) #check
    scratch_dir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))  #check
    name_prefix: str = field(default='users_analysis')
    display_output: bool = field(default=True)
    no_save_output: bool = field(default=False)
    save_to_geddes: bool = field(default=False)
    bucket_name: str = field(default='nanohub.processed')
    object_path: str = field(init = False)

    #classroom detection behavior (xufeng)
    class_activity_tol: int = field(default=2)
    class_attention_span: int = field(default=3)
    class_size_min: int = field(default=5)
    class_distance_threshold: int = field(default =50)
    class_merge_time_threshold: int = field(default=120)
    class_merge_distance_threshold: int = field(default=5)

    #quick cost-based cluster analysis
    costSizeMin: int = field(default=4)
    cost_force_all_diff_lvl: int = field(default=501)
    cost_tolerance: int = field(default=57)

    #dask
    dask_scheduler: str = field(default='single-threaded')

    #internal options
    CI: bool = field(default=False) #check
    CI_dir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI')) #use os.getcwd() instead of os.path.dirname(os.path.realpath(__file__)) for jupyter
    generate_notebook_checkpoints: bool = field(default=True)
    gather_data_only: bool = field(default=False) #check
    use_old_data: bool = field(default=False) #check
    log_level: str = field(default='INFO')


class ExecuteAlgorithmCommandFactory:
    def create_new(task: str, start_date: str, end_date: str) -> ExecuteAlgorithmCommand:
        command = ExecuteAlgorithmCommand(task, start_date, end_date)
        return command



class IGenerateSemesterTimeFrames:
    def create_timeframe_list(self, start_date: datetime.date, end_date: datetime.date) -> [(
            datetime.date, datetime.date
    )]:
        raise NotImplementedError


class TwoSemesterTimeFrameGenerator(IGenerateSemesterTimeFrames):
    def __init__(
            self, fall_start_month: str = '07', spring_start_month: str = '01', fall_start_date: str = '02',  spring_start_date: str = '01'
    ):
        self.fall_start_month = fall_start_month
        self.spring_start_month = spring_start_month
        self.fall_start_date = fall_start_date
        self.spring_start_date = spring_start_date

    def determine_semester(self, temp_date: datetime.date) -> datetime.date:
        year_hold = temp_date.year
        if temp_date < date(year_hold, int(self.fall_start_month), int(self.fall_start_date)):
            date1 = date(temp_date.year, int(self.fall_start_month), int(self.fall_start_date))
            return date1
        elif temp_date >= date(year_hold, int(self.fall_start_month), int(self.fall_start_date)):
            date2 = date(int(temp_date.year) + 1, int(self.spring_start_month), int(self.spring_start_date))
            return date2

    def create_timeframe_list(self, start_date: datetime.date, end_date: datetime.date) -> [(
            datetime.date, datetime.date
    )]:

        timeframe = []
        start = start_date
        stop = self.determine_semester(start)
        while True:
            timeframe.append([start, stop])
            # print(str(start) + ", " + str(stop))
            start = stop
            stop = self.determine_semester(start)
            if stop > end_date:
                timeframe.append([start, end_date])
                break

        return timeframe


def cluster_by_time_list(task: str, timelist: dict) -> [(int, pd.DataFrame)]:
    df_list = []

    timelist = {
        '1': ['2006-01-01', '2006-07-02'],
        '2': ['2006-07-02', '2007-01-01']
    }

    for x in range(len(timelist)):
        start, end = timelist[x]
        df_list.append((x, ExecuteAlgorithmCommandFactory.create_new(task, start, end)))

    return df_list


#command -> ClusteringFlags
def run_clustering(command) -> pd.DataFrame:
    handler = create_default_handler(command.log_level)
    return handler.handle(command)


def create_default_handler(log_level):
    numeric_level = getattr(logging, log_level.upper(), 10)
    logging.basicConfig(level=numeric_level, format='%(message)s')
    _l = logging.getLogger()

    return ValidationHandler(
        [DateValidator()],
        GeddesSaver(
            DisplayDf(
                DataframeLogger(
                    AlgorithmHandler(AlgorithmsMap(), _l), _l
                ), _l
            ), _l
        ), _l
    )



# if __name__ == '__main__':
#     #datetime parsing in alg file to view for checking enddate is later than startdate
#     command = ExecuteAlgorithmCommandFactory.create_new('mike', '2006-01-01', '2007-07-02')
#     run_clustering(command)
