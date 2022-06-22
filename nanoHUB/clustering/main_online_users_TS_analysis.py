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
from run_clustering import ClusteringFlags

#I want to turn the parameter into an object that you can call like flags.time or flags.task
#When the object is created, I want the useless flags to default to false, so that if someone wants to use it quick they don't have to worry about it

#how would you have done it?


# if __name__ == '__main__':
#     start = time.time()
#     main_online_users_TS_analysis()
#     end = time.time()
#     print("Time:", end - start)
