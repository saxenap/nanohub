import argparse
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


def main_online_users_TS_analysis(inparams) -> pd.DataFrame:
    #
    # Analysis:
    #

    #task selection
    ###
    if inparams.task == 'classroom_detection' or inparams.task == 'xufeng':
        # classroom detection
        func = core_classroom_analysis

    elif inparams.task == 'cost_cluster_analysis' or inparams.task == 'mike':
        # quick cost-function clustering analysis

        ###
        if inparams.cost_probe_range == 'all':
            raise NotImplementedError("This functionality is yet to be implemented.")

        inparams.class_probe_range = inparams.cost_probe_range
        ###
        func = core_cost_cluster_analysis

    else:
        raise ValueError("A task must be assigned using --task option. See help (-h) for more information.")
    ###

    #unsure
    numeric_level = getattr(logging, inparams.log_level.upper(), 10)
    logging.basicConfig(level=numeric_level, format='%(message)s')
        # summarize input options
    #unsure

    #cleaned data/live data
    if inparams.CI:
        # CI/Test runs
        # The only difference here should be CI/Test runs use sample,
        # cleaned data instead of live SQL data


        logging.info('GitLab CI runs')

        # setting the default time range for CI
        inparams.class_probe_range = '2018-1-1:2018-5-1'
        logging.info('Setting analysis time range to CI default: ' + inparams.class_probe_range)
    #cleaned data/live data

    #timeframe
    if inparams.class_probe_range == 'latest':
        # probes only the latest (today - 2 STD of Gaussian attention window function)
        # Each user simulation run action is expanded to 1 STD, and therefore the resulting cluster has max width of 2 STD
        inparams.data_probe_range = [datetime.date.today() - datetime.timedelta(days=inparams.class_attention_span * 2),
                                     datetime.date.today()]
        inparams.class_probe_range = [x.strftime("%Y-%m-%d") for x in inparams.data_probe_range]

    else:
        # probes given time range
        # expects inparams.class_probe_range in form of, for example, '2018-1-1:2018-5-1'
        inparams.class_probe_range = inparams.class_probe_range.split(':')
        inparams.data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in inparams.class_probe_range]
    #timeframe

    #
    # Preparations
    #

    #checks to see if bucket/path are valid
    if inparams.save_to_geddes:
        if inparams.bucket_name is None or inparams.bucket_name == '':
            raise ValueError("A bucket name is necessary in order to save results to Geddes")
        if inparams.object_path is None or inparams.object_path == '':
            raise ValueError("An object path is necessary in order to save results to Geddes")
    # checks to see if bucket/path are valid

    # create scratch directory if it does not exist
    if not os.path.exists(get_scratch_dir(inparams)):
        logging.info('Creating new scratch directory: ' + get_scratch_dir(inparams))
        os.mkdir(get_scratch_dir(inparams))

    if inparams.no_save_output:
        logging.info("Skipping saving output locally ...")

    if not inparams.save_to_geddes:
        logging.info("Skipping saving output to Geddes ...")

    if not inparams.use_old_data:
        logging.info('Gathering data  ......')
        gather_data(inparams) #unsure
        if inparams.gather_data_only:
            return
    else:
        logging.info('Option "--user_old_data" enabled. Using data from previous run ......')

    logging.debug(pformat(vars(inparams)))

    final_clusters_df = func(inparams) #runs clustering

    return final_clusters_df

# if __name__ == '__main__':
#     start = time.time()
#     main_online_users_TS_analysis()
#     end = time.time()
#     print("Time:", end - start)
