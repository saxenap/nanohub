import os
from dataclasses import dataclass, field
from datetime import datetime, date
from algorithms_map import AlgorithmsMap
from pprint import pprint, pformat
import pandas as pd
import logging

from preprocessing.gather_data import gather_data
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from core_quick_cluster_detection.core_cost_cluster_analysis import core_cost_cluster_analysis, get_scratch_dir
from save_clusters_to_geddes import save_clusters_to_geddes
from algorithms_map import (
    DateValidator, AlgorithmsMap, AlgorithmHandler, GeddesSaver, DisplayDf, DataframeLogger, ValidationHandler
)


@dataclass
class ExecuteAlgorithmCommand:
    #general
    task: str
    start_date: str #datetimeformat: ####-##-##
    end_date: str #datetimeformat: ####-##-##
    class_probe_range: str = field(init = False)

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
    
    def __post_init__(self):
        if not self.class_probe_range:
            self.class_probe_range = self.start_date + ":" + self.end_date

        self.class_probe_range = self.class_probe_range.split(':')
        self.data_probe_range = [datetime.strptime(x, '%Y-%m-%d') for x in self.class_probe_range]

        self.objectPath = 'clusters/${' + self.task + '}/by_semester'
        if not os.path.exists(get_scratch_dir(self)):
            logging.info('Creating new scratch directory: ' + get_scratch_dir(self))
        os.mkdir(get_scratch_dir(self))


def cluster_by_semester(command):
    df_list = []

    # start_dt = datetime.strptime(command.start_date, '%Y-%m-%d')
    # sem1 = year + '-01-01'
    # sem2 = year + '-07-02'
    yield run_clustering(command)


#command -> ClusteringFlags
def run_clustering(command) -> pd.DataFrame:
    handler = create_default_handler(command)
    return handler.handle(command)


def create_default_handler(command):
    numeric_level = getattr(logging, command.log_level.upper(), 10)
    logging.basicConfig(level=numeric_level, format='%(message)s')
    _l = logging.getLogger()

    return ValidationHandler(
        [DateValidator()],
        GeddesSaver(
            DisplayDf(
                DataframeLogger(
                    AlgorithmHandler(
                        AlgorithmsMap(), _l
                    ), _l
                ), _l
            ), _l
        ), _l
    )


if __name__ == '__main__':
    #datetime parsing in alg file to view for checking enddate is later than startdate
    command = ExecuteAlgorithmCommand('mike', '2006-01-01', '2007-07-02')
    run_clustering(command)
