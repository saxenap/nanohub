import argparse
from pprint import pprint, pformat
import code
import os
import time

from datetime import date 
import logging

from preprocessing.gather_data import gather_data
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from core_quick_cluster_detection.core_cost_cluster_analysis import core_cost_cluster_analysis

def main_online_users_TS_analysis():

    parser = argparse.ArgumentParser(description='Online user weblog time series analysis originally designed for nanoHUB.org')
    
    # task options
    parser.add_argument('--task', help='specific task', 
                                  action='store', default='classroom_detection')
                                             
    # SQL connection
    parser.add_argument('--SQL_username', help='SQL database username', 
                                         action='store', default='wang2506_ro')
    parser.add_argument('--SQL_password', help='SQL password', 
                                         action='store', default='fnVnwcCS7iT45EsA')
    parser.add_argument('--SQL_addr', help='SQL address', 
                                         action='store', default='127.0.0.1')
    parser.add_argument('--SQL_port', help='SQL port', 
                                         action='store', default='3306')

    # data
    parser.add_argument('--geoip2_mmdb_filepath', help='full file path of mmdb file from GeoIP2', 
                                         action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb'))
                                                                                                                       
    # directories
    parser.add_argument('--output_dir', help='location of output directory for output files', 
                                         action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')) 
    parser.add_argument('--scratch_dir', help='location of scratch directory for temporary files', 
                                         action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp')) 
    parser.add_argument('--name_prefix', help='prefix to all output files', 
                                         action='store', default='users_analysis')

    # class room detection behavior
    parser.add_argument('--class_probe_range', help='classroom detection: date range of the class to be analyzed. For example, 2018-1-1:2018-5-1', 
                                                action='store', default='latest')#'2020-9-25:2020-10-13')
    parser.add_argument('--class_activity_tol', help='classroom detection: minimal days apart to declare two use of same tool as separate activity blocks', 
                                                action='store', default=2)
    parser.add_argument('--class_attention_span', help='classroom detection: the standard deviation of gaussian shaped attention window function', 
                                                action='store', default=3)
    parser.add_argument('--class_size_min', help='classroom detection: minimal number of users within a cluster to declare it as a valid class', 
                                            action='store', default=5)
    parser.add_argument('--class_distance_threshold', help='classroom detection: maximum intra-cluster distance in km for geospatial clusters', 
                                            action='store', default=50)
    parser.add_argument('--class_merge_time_threshold', help='classroom detection: when merging similar clusters, maximum time range allowed for merging', 
                                            action='store', default=120)
    parser.add_argument('--class_merge_distance_threshold', help='classroom detection: when merging similat cluster, maximum intra-cluster distance in km for geospatial clusters', 
                                            action='store', default=5)
                                            
    # quick cost-based cluster analysis
    parser.add_argument('--cost_probe_range', help='classroom detection: date range of the class to be analyzed. For example, 2018-1-1:2018-5-1', 
                                                action='store', default='all')    
    parser.add_argument('--cost_size_min', help='classroom detection: minimal cluster size', 
                                                action='store', default=4)
    parser.add_argument('--cost_force_all_diff_lvl', help='classroom detection: forceAllDifferencesLevel', 
                                                action='store', default=501)
    parser.add_argument('--cost_tolerance', help='classroom detection: tolerance', 
                                                action='store', default=57)
                                                                                                                                                                                          
    # dask
    parser.add_argument('--dask_scheduler', help='dask scheduler: "threads"/"processes"/"single-threaded"', 
                                            action='store', default="single-threaded")
                                            
    # internal options
    parser.add_argument('--CI', help='start GitLab CI pipeline', 
                                action='store_true')
    parser.add_argument('--CI_dir', help='location of CI directory', 
                                    action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI'))
    parser.add_argument('--generate_notebook_checkpoints', help='shelve variables in order to connect with notebooks at various points', 
                                    action='store_true')
    parser.add_argument('--use_old_data', help='use feature data from previous run', 
                                    action='store_true')                                                   
    inparams = parser.parse_args()
    
    # redefine inparams for cronjob smoothness - since we use this setting anyway    
    inparams.generate_notebook_checkpoints = True #so outputs are saved
    
    
    # summarize input options
    if inparams.CI:
        # CI/Test runs
        # The only difference here should be CI/Test runs use sample, 
        # cleaned data instead of live SQL data
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        
        logging.info('GitLab CI runs')
        
        # setting the default time range for CI
        inparams.class_probe_range='2018-1-1:2018-5-1'
        logging.info('Setting analysis time range to CI default: '+inparams.class_probe_range)
        
    else:
        # Production runs
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        pass
    
    # import datetime
    # now = datetime.datetime.now()
    # delta = datetime.timedelta(days=14)
    # prev = now-delta
    # start_d = '{}-{}-{}'.format(str(prev.year),str(prev.month),str(prev.day))
    # end_d = '{}-{}-{}'.format(str(now.year),str(now.month),str(now.day))
    # inparams.class_probe_range=start_d+':'+end_d #'2018-1-1:2018-5-1'
    

    # display parameters but censor password
    if 'SQL_password' in inparams:
        temp_real_password = inparams.SQL_password   
        inparams.SQL_password = ''.join(['*' for x in inparams.SQL_password])
                 
    logging.info(pformat(vars(inparams)))
    inparams.SQL_password = temp_real_password
    del temp_real_password
    
    #
    # Preparations
    #

    # create scratch directory if it does not exist
    if not os.path.exists(inparams.scratch_dir):
        logging.info('Creating new scratch directory: '+inparams.scratch_dir)
        os.mkdir(inparams.scratch_dir)

    # create output directory if it does not exist
    if not os.path.exists(inparams.output_dir):
        logging.info('Creating new output directory: '+inparams.output_dir)
        os.mkdir(inparams.output_dir)
            
    if not inparams.use_old_data:
        gather_data(inparams)
    else:
        logging.info('Option "--user_old_data" enabled. Using data from previous run ......')

    #
    # Analysis:
    #
    
    if 'classroom_detection' in inparams.task:
        # classroom detection
        core_classroom_analysis(inparams)

    if 'cost_cluster_analysis' in inparams.task:
        # quick cost-function clustering analysis
        core_cost_cluster_analysis(inparams)



                            
if __name__ == '__main__':
    start = time.time()
    main_online_users_TS_analysis()
    end = time.time()
    print("Time:", end - start)