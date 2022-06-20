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
from save_clusters_to_geddes import save_clusters_to_geddes

#I want to turn the parameter into an object that you can call like flags.time or flags.task
#When the object is created, I want the useless flags to default to false, so that if someone wants to use it quick they don't have to worry about it

#how would you have done it?

def main_online_users_TS_analysis(flags) -> pd.DataFrame:
    print(flags.firstYear)
    # class_probe_range = flags.firstYear + ':' + flags.lastYear
    #
    # Analysis:
    #

    #task selection
    ###
    if flags.task == 'classroom_detection' or flags.task == 'xufeng':
        # classroom detection
        func = core_classroom_analysis

    elif flags.task == 'cost_cluster_analysis' or flags.task == 'mike':
        # quick cost-function clustering analysis

        func = core_cost_cluster_analysis

    else:
        raise ValueError("A task must be assigned.")

    # numeric_level = getattr(logging, inparams.log_level.upper(), 10)
    # logging.basicConfig(level=numeric_level, format='%(message)s')
    #     # summarize input options

    #cleaned data/live data
    if flags.CI:
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
        class_probe_range = flags.class_probe_range.split(':')
        data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in class_probe_range]
    #timeframe

    #moved above 2 lines out of else:

    #
    # Preparations
    #

    #checks to see if bucket/path are valid
    if flags.save_to_geddes:
        if flags.bucketName is None or flags.bucketName == '':
            raise ValueError("A bucket name is necessary in order to save results to Geddes")
        if flags.objectPath is None or flags.objectPath == '':
            raise ValueError("An object path is necessary in order to save results to Geddes")
    # checks to see if bucket/path are valid

    # # create scratch directory if it does not exist
    if not os.path.exists(get_scratch_dir(flags)):
        logging.info('Creating new scratch directory: ' + get_scratch_dir(flags))
        os.mkdir(get_scratch_dir(flags))

    if flags.noSaveOutput:
        logging.info("Skipping saving output locally ...")

    if not flags.saveToGeddes:
        logging.info("Skipping saving output to Geddes ...")

    if not flags.useOldData:
        # logging.info('Gathering data  ......')
        gather_data(flags) #unsure how to handle with current solution
        if flags.gatherDataOnly:
            return
    else:
        logging.info('Option "--user_old_data" enabled. Using data from previous run ......')

    logging.debug(pformat(vars(flags)))

    final_clusters_df = func(flags) #runs clustering

    if flags.saveToGeddes == True:
        save_clusters_to_geddes(final_clusters_df, flags.bucketName, flags.class_probe_range, flags.objectPath)

    return final_clusters_df

# if __name__ == '__main__':
#     start = time.time()
#     main_online_users_TS_analysis()
#     end = time.time()
#     print("Time:", end - start)
