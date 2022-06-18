from pprint import pprint, pformat
import code
import os
import time
import pandas as pd

from datetime import date
import logging
import datetime

from preprocessing.gather_data import gather_data
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from core_quick_cluster_detection.core_cost_cluster_analysis import core_cost_cluster_analysis, get_scratch_dir

#I want to turn the parameter into an object that you can call like flags.time or flags.task
#When the object is created, I want the useless flags to default to false, so that if someone wants to use it quick they don't have to worry about it

#how would you have done it?

def main_online_users_TS_analysis(task, firstyear, lastyear, bucket_name, object_path, save_to_geddes: bool, use_old_data: bool, gather_data_only: bool) -> pd.DataFrame:

    firstyear = firstyear + "-01-01"  # semester 1
    lastyear = lastyear + "-07-02"  # semester 2
    class_probe_range = firstyear + ":" + lastyear
    if bucket_name == '':
        bucket_name = 'nanohub.processed'
    if object_path == '':
        object_path = 'clusters/${' + task + '}/by_semester'

    #
    # Analysis:
    #

    #task selection
    ###
    if task == 'classroom_detection' or task == 'xufeng':
        # classroom detection
        func = core_classroom_analysis

    elif task == 'cost_cluster_analysis' or task == 'mike':
        # quick cost-function clustering analysis

        func = core_cost_cluster_analysis

    else:
        raise ValueError("A task must be assigned.")

    # numeric_level = getattr(logging, inparams.log_level.upper(), 10)
    # logging.basicConfig(level=numeric_level, format='%(message)s')
    #     # summarize input options

    # #cleaned data/live data
    # if inparams.CI:
    #     # CI/Test runs
    #     # The only difference here should be CI/Test runs use sample,
    #     # cleaned data instead of live SQL data
    #
    #
    #     logging.info('GitLab CI runs')
    #
    #     # setting the default time range for CI
    #     inparams.class_probe_range = '2018-1-1:2018-5-1'
    #     logging.info('Setting analysis time range to CI default: ' + inparams.class_probe_range)
    # #cleaned data/live data

    #timeframe
    # if inparams.class_probe_range == 'latest':
    #     # probes only the latest (today - 2 STD of Gaussian attention window function)
    #     # Each user simulation run action is expanded to 1 STD, and therefore the resulting cluster has max width of 2 STD
    #     inparams.data_probe_range = [datetime.date.today() - datetime.timedelta(days=inparams.class_attention_span * 2),
    #                                  datetime.date.today()]
    #     inparams.class_probe_range = [x.strftime("%Y-%m-%d") for x in inparams.data_probe_range]

    # else:
        # probes given time range
        # expects inparams.class_probe_range in form of, for example, '2018-1-1:2018-5-1'
    class_probe_range = class_probe_range.split(':')
    data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in class_probe_range]
    #timeframe

    #moved above 2 lines out of else:

    #
    # Preparations
    #

    #checks to see if bucket/path are valid
    if save_to_geddes:
        if bucket_name is None or bucket_name == '':
            raise ValueError("A bucket name is necessary in order to save results to Geddes")
        if object_path is None or object_path == '':
            raise ValueError("An object path is necessary in order to save results to Geddes")
    # checks to see if bucket/path are valid

    # # create scratch directory if it does not exist
    # if not os.path.exists(get_scratch_dir(inparams)):
    #     logging.info('Creating new scratch directory: ' + get_scratch_dir(inparams))
    #     os.mkdir(get_scratch_dir(inparams))
    #
    # if inparams.no_save_output:
    #     logging.info("Skipping saving output locally ...")
    #
    # if not inparams.save_to_geddes:
    #     logging.info("Skipping saving output to Geddes ...")

    if not use_old_data:
        # logging.info('Gathering data  ......')
        gather_data(inparams) #unsure how to handle with current solution
        if gather_data_only:
            return
    # else:
    #     logging.info('Option "--user_old_data" enabled. Using data from previous run ......')

    # logging.debug(pformat(vars(inparams)))

    final_clusters_df = func(inparams) #runs clustering

    return final_clusters_df

# if __name__ == '__main__':
#     start = time.time()
#     main_online_users_TS_analysis()
#     end = time.time()
#     print("Time:", end - start)
