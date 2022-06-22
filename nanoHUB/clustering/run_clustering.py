import os
from dataclasses import dataclass, field
import pandas as pd
import logging
from nanoHUB.clustering.algorithms_map import (
    DateValidator, AlgorithmsMap, AlgorithmHandler, GeddesSaver, DisplayDf, DataframeLogger, ValidationHandler, LocalDriveSaver
)


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
        

def cluster_by_semester(command) -> []:
    df_list = []

    # start_dt = datetime.strptime(command.start_date, '%Y-%m-%d')
    # sem1 = year + '-01-01'
    # sem2 = year + '-07-02'
    for sem in semesters:
        df_list.append(run_clustering(command))

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
