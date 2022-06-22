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

@dataclass
class ClusteringFlags:
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
    makefile: bool = field(default=False)
    
    def __post_init__(self):
        self.class_probe_range = self.start_date + ":" + self.end_date
        self.objectPath = 'clusters/${' + self.task + '}/by_semester'

def cluster_by_semester(flags):
    df_list = []

    # start_dt = datetime.strptime(flags.start_date, '%Y-%m-%d')
    # sem1 = year + '-01-01'
    # sem2 = year + '-07-02'
    yield run_clustering(flags)

#flags -> ClusteringFlags
def run_clustering(flags) -> pd.DataFrame:
    _map = AlgorithmsMap()
    validate_flags(flags, _map)
    maybe_save_raw_data(flags)
    if flags.gather_data_only:
        return
    # final_df = main_online_users_TS_analysis(flags)
    func = getattr(_map, flags.task)
    print(type(func))
    print(func)
    final_clusters_df = func(flags) #runs clustering

    if flags.save_to_geddes == True:
        save_clusters_to_geddes(final_clusters_df, flags)

    return final_clusters_df



def maybe_save_raw_data(flags: ClusteringFlags) -> None:
    if flags.use_old_data == False:
        logging.info('Gathering data  ......')
        gather_data(flags) #unsure how to handle with current solution
    else:
        logging.info('Option "--user_old_data" enabled. Using data from previous run ......')

    logging.debug(pformat(vars(flags)))



def validate_flags(flags: ClusteringFlags, _map: AlgorithmsMap) -> None:

    #
    # Analysis:
    #
    #
    
    # Algorithm Validation
    if not hasattr(_map, flags.task):
        raise Exception(
            "Invalid Algorithm/Task. Valid algorithms/tasks are: %s" %_map
        )

    # Date Validation
    if not flags.makefile:
        start_check = datetime.strptime(flags.start_date, '%Y-%m-%d')
        end_check = datetime.strptime(flags.end_date, '%Y-%m-%d')

        if not start_check < end_check:
            raise Exception("start_date before end_date")

    #task selection
    ###
    if flags.task == 'core_classroom_analysis' or flags.task == 'xufeng':
        # classroom detection
        func = core_classroom_analysis

    elif flags.task == 'core_cost_cluster_analysis' or flags.task == 'mike':
        # quick cost-function clustering analysis

        func = core_cost_cluster_analysis

    else:
        raise ValueError("A task must be assigned.")

    numeric_level = getattr(logging, flags.log_level.upper(), 10)
    logging.basicConfig(level=numeric_level, format='%(message)s')
        # summarize input options

    #cleaned data/live data
    if flags.CI == True:
        # CI/Test runs
        # The only difference here should be CI/Test runs use sample,
        # cleaned data instead of live SQL data


        logging.info('GitLab CI runs')

        # setting the default time range for CI
        flags.class_probe_range = '2018-1-1:2018-5-1'
        logging.info('Setting analysis time range to CI default: ' + flags.class_probe_range)
    #cleaned data/live data
    print(flags.class_probe_range)
    #timeframe
    if flags.class_probe_range == 'latest':
        # probes only the latest (today - 2 STD of Gaussian attention window function)
        # Each user simulation run action is expanded to 1 STD, and therefore the resulting cluster has max width of 2 STD
        flags.data_probe_range = [datetime.date.today() - datetime.timedelta(days=flags.class_attention_span * 2),
                                     datetime.date.today()]
        flags.class_probe_range = [x.strftime("%Y-%m-%d") for x in flags.data_probe_range]

    else:
        # probes given time range
        # expects inparams.class_probe_range in form of, for example, '2018-1-1:2018-5-1'
        flags.class_probe_range = flags.class_probe_range.split(':')
        flags.data_probe_range = [datetime.strptime(x, '%Y-%m-%d') for x in flags.class_probe_range]
    #timeframe

    #
    # Preparations
    #

    #checks to see if bucket/path are valid
    if flags.save_to_geddes:
        if flags.bucket_name is None or flags.bucket_name == '':
            raise ValueError("A bucket name is necessary in order to save results to Geddes")
        if flags.object_path is None or flags.object_path == '':
            raise ValueError("An object path is necessary in order to save results to Geddes")
    # checks to see if bucket/path are valid

    # # create scratch directory if it does not exist
    if not os.path.exists(get_scratch_dir(flags)):
        logging.info('Creating new scratch directory: ' + get_scratch_dir(flags))
        os.mkdir(get_scratch_dir(flags))

    if flags.no_save_output == True:
        logging.info("Skipping saving output locally ...")

    if flags.save_to_geddes == False:
        logging.info("Skipping saving output to Geddes ...")

    
# if __name__ == '__main__':
#     lol = "python3 main_online_users_TS.py " + \
#           "--cost_probe_range " + 'firstyear' + ":" + 'lastyear' + " " + \
#           "--class_probe_range " + 'firstyear' + ":" + 'lastyear' + " " + \
#           "--task $(" + 'task' + ") " + \
#           "--bucket_name $(" + 'bucketname' + ") " + \
#           "--object_path $(" + 'objectpath' + ") " + \
#           "--log_level $(" + 'loglevel' + ") " + \
#           "(other_flags)"
#     print(lol) #

if __name__ == '__main__':
    #datetime parsing in alg file to view for checking enddate is later than startdate
    run_clustering(ClusteringFlags('mike', '2006-01-01', '2007-07-02'))
