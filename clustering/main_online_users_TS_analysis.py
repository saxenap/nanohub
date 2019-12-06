import argparse
from pprint import pprint, pformat
import code
import os

import logging

from preprocessing.gather_data import gather_data
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis

def main_online_users_TS_analysis():

    parser = argparse.ArgumentParser(description='Online user weblog time series analysis originally designed for nanoHUB.org')
    
    # SQL connection
    parser.add_argument('--SQL_username', help='SQL database username', 
                                         action='store', default='invalid SQL username')
    parser.add_argument('--SQL_password', help='SQL password', 
                                         action='store', default='invalid SQL password')
    parser.add_argument('--SQL_addr', help='SQL address', 
                                         action='store', default='127.0.0.1')
    parser.add_argument('--SQL_port', help='SQL port', 
                                         action='store', default='3306')
                                                                                                                       
    # directories
    parser.add_argument('--scratch_dir', help='location of scratch directory for temporary files', 
                                         action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))
                                    
    # internal options
    parser.add_argument('--CI', help='start GitLab CI pipeline', 
                                action='store_true')
    parser.add_argument('--CI_dir', help='location of CI directory', 
                                    action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI'))
               
    inparams = parser.parse_args()       

    
    # summarize input options
    if inparams.CI:
        # CI/Test runs
        # The only difference here should be CI/Test runs use sample, 
        # cleaned data instead of live SQL data
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        
        logging.info('GitLab CI runs')
        
    else:
        # Production runs
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        pass
    
    # display parameters but censor password
    display_inparams = inparams
    if 'SQL_password' in display_inparams:
        display_inparams.SQL_password = ''.join(['*' for x in display_inparams.SQL_password])
        
    logging.info(pformat(vars(inparams)))
    
    #
    # Preparations
    #
    
    # create scratch directory if it does not exist
    if not os.path.exists(inparams.scratch_dir):
        logging.info('Creating new scratch directory: '+inparams.scratch_dir)
        os.mkdir(inparams.scratch_dir)
    
    
    #
    # Analysis: classroom detection
    #
                    
    # prepare data
    gather_data(inparams)
    
    # classroom detection
    core_classroom_analysis(inparams)
                            
if __name__ == '__main__':
    main_online_users_TS_analysis() 
