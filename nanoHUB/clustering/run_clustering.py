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
    firstDate: str #datetimeformat: ####-##-##
    lastDate: str #datetimeformat: ####-##-##
    class_probe_range: str = field(init = False)

    #data
    geoip2_mmdb_filepath: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb')) #check

    #directories
    outputDir: str = field(default = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')) #check
    scratchDir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))  #check
    namePrefix: str = field(default='users_analysis')
    displayOutput: bool = field(default=True)
    noSaveOutput: bool = field(default=False)
    saveToGeddes: bool = field(default=False)
    bucketName: str = field(default='nanohub.processed')
    objectPath: str = field(init = False)

    #classroom detection behavior (xufeng)
    classActivityTol: int = field(default=2)
    classAttentionSpan: int = field(default=3)
    classSizeMin: int = field(default=5)
    classDistanceThreshold: int = field(default =50)
    classMergeTimeThreshold: int = field(default=120)
    classMergeDistanceThreshold: int = field(default=5)

    #quick cost-based cluster analysis
    costSizeMin: int = field(default=4)
    costForceAllDiffLvl: int = field(default=501)
    costTolerance: int = field(default=57)

    #dask
    daskScheduler: str = field(default='single-threaded')

    #internal options
    CI: bool = field(default=False) #check
    CI_dir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI')) #use os.getcwd() instead of os.path.dirname(os.path.realpath(__file__)) for jupyter
    generateNotebookCheckpoints: bool = field(default=True)
    gatherDataOnly: bool = field(default=False) #check
    useOldData: bool = field(default=False) #check
    logLevel: str = field(default='INFO')
    
    def __post_init__(self):
        self.class_probe_range = self.firstDate + ":" + self.lastDate
        self.objectPath = 'clusters/${' + self.task + '}/by_semester'

def cluster_by_semester(flags):
    df_list = []

#flags -> ClusteringFlags
def run_clustering(flags) -> pd.DataFrame:
    _map = AlgorithmsMap()
    validate_flags(flags, _map)
    maybe_save_raw_data(flags)
    if flags.gatherDataOnly:
        return
    # final_df = main_online_users_TS_analysis(flags)
    func = getattr(_map, flags.task)

    final_clusters_df = func(flags) #runs clustering

    if flags.saveToGeddes == True:
        save_clusters_to_geddes(final_clusters_df, flags)

    return final_clusters_df



def maybe_save_raw_data(flags: ClusteringFlags) -> None:
    if flags.useOldData == False:
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
            "Invalid Algorithm/Task. Valid algorithms/tasks are: %s" % _map
        )

    # Date Validation
    startCheck = datetime.strptime(flags.startDate, '%Y-%m-%d')
    endCheck = datetime.strptime(flags.endDate, '%Y-%m-%d')

    if not startCheck < endCheck:
        raise Exception("startDate before endDate")

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

    numeric_level = getattr(logging, flags.logLevel.upper(), 10)
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
        flags.data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in flags.class_probe_range]
    #timeframe

    #
    # Preparations
    #

    #checks to see if bucket/path are valid
    if flags.saveToGeddes:
        if flags.bucketName is None or flags.bucketName == '':
            raise ValueError("A bucket name is necessary in order to save results to Geddes")
        if flags.objectPath is None or flags.objectPath == '':
            raise ValueError("An object path is necessary in order to save results to Geddes")
    # checks to see if bucket/path are valid

    # # create scratch directory if it does not exist
    if not os.path.exists(get_scratch_dir(flags)):
        logging.info('Creating new scratch directory: ' + get_scratch_dir(flags))
        os.mkdir(get_scratch_dir(flags))

    if flags.noSaveOutput == True:
        logging.info("Skipping saving output locally ...")

    if flags.saveToGeddes == False:
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
