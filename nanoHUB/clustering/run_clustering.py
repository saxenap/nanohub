import os
from dataclasses import dataclass, field
from datetime import datetime, date
import pandas as pd
import logging
from pathlib import Path

from nanoHUB.clustering.algorithms_map import (
    DateValidator, AlgorithmsMap, AlgorithmHandler, GeddesSaver, DisplayDf, DataframeLogger, ValidationHandler, LocalDriveSaver
)
from mpire import WorkerPool
from mpire.dashboard import connect_to_dashboard


@dataclass
class ExecuteAlgorithmCommand:
    #general
    task: str
    start_date: str #datetimeformat: ####-##-##
    end_date: str #datetimeformat: ####-##-##
    class_probe_range: str = field(init=False)

    #data
    geoip2_mmdb_filepath: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb'))

    #directories
    output_dir: str = field(default = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output'))
    scratch_dir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))
    name_prefix: str = field(default='users_analysis')
    display_output: bool = field(default=True)
    no_save_output: bool = field(default=False) #saves on default
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
    cost_size_min: int = field(default=4)
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

    def __post_init__(self):
        self.class_probe_range = self.start_date + ':' + self.end_date
        print(self.__dict__)
        exit(0)


class ExecuteAlgorithmCommandFactory:
    def create_new(task: str, start_date: str, end_date: str) -> ExecuteAlgorithmCommand:
        command = ExecuteAlgorithmCommand(task, start_date, end_date)
        return command



class IGenerateTimeFrames:
    def create_timeframe_list(self, start_date: datetime.date, end_date: datetime.date) -> [(
            datetime.date, datetime.date
    )]:
        raise NotImplementedError


class TwoSemesterTimeFrameGenerator(IGenerateTimeFrames):
    def __init__(
            self,
            fall_start_month: int = 7,
            spring_start_month: int = 1,
            fall_start_date: int = 2,
            spring_start_date: int = 1
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
            last = start
            start = stop
            stop = self.determine_semester(start)
            print(start, stop)
            if stop > end_date:
                if start < end_date:
                    timeframe.append([start, end_date])
                break

        return timeframe

    def timeframe_to_str(self, timeframe_list: [(datetime.date, datetime.date)]) -> [str, str]:
        str_timeframe = []
        for x in timeframe_list:
            str_timeframe.append([
                str(x[0].year) + "-" + str(x[0].month).rjust(2, '0') + "-" + str(x[0].day).rjust(2, '0'),
                str(x[1].year) + "-" + str(x[1].month).rjust(2, '0') + "-" + str(x[1].day).rjust(2, '0')
            ])
        return str_timeframe

    def timeframe_to_command(self, task, timeframe_str_list):
        command_list = []

        for timeframe in timeframe_str_list:
            start, end = timeframe
            command_list.append(ExecuteAlgorithmCommandFactory.create_new(task, start, end))

        return command_list

    def cluster_for_start_end(self, task, start, end):
        alg_df_list = []

        timeframe_list = TwoSemesterTimeFrameGenerator().create_timeframe_list(start, end)
        timeframe_str_list = TwoSemesterTimeFrameGenerator().timeframe_to_str(timeframe_list)
        command_list = TwoSemesterTimeFrameGenerator().timeframe_to_command(task, timeframe_str_list)
        df_list = cluster_by_command(command_list)

        return df_list

    def cluster_for_all(self, init_year: int = 2006, init_month: int = 1, init_day: int = 1):
        alg_df_list = []
        start = date(init_year, init_month, init_day)
        present = datetime.now().date()

        # get algs from algorithms_map
        alg_list = AlgorithmsMap().return_algorithms()

        for alg in alg_list:
            timeframe_list = TwoSemesterTimeFrameGenerator().create_timeframe_list(start, present)
            timeframe_str_list = TwoSemesterTimeFrameGenerator().timeframe_to_str(timeframe_list)
            command_list = TwoSemesterTimeFrameGenerator().timeframe_to_command(alg, timeframe_str_list)
            df_list = cluster_by_command(command_list)
            alg_df_list.append(df_list)


def cluster_by_command(command_list: [ExecuteAlgorithmCommand]) -> [(int, pd.DataFrame)]:
    df_list = []
    cores = 1
    # if int(os.cpu_count() * .7) < 5:
    #     cores = int(os.cpu_count() * .7)
    # else:
    #     cores = 5

    with WorkerPool(n_jobs=cores, daemon=False) as pool: #15 cores is max tested sucessfully on windows, 6 on arm64
        df_list.append(pool.map(run_clustering, command_list))

    return df_list
    #need to fix banner_timeout issue, happens when you run too many requests/too many cores. We are limited by requests.


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
            LocalDriveSaver(
                DisplayDf(
                    DataframeLogger(
                        AlgorithmHandler(AlgorithmsMap(), _l), _l
                    ), _l
                ), _l
            ), _l
        ), _l
    )


if __name__ == '__main__':
    result = TwoSemesterTimeFrameGenerator().cluster_for_all()