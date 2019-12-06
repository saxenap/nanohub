import argparse
from pprint import pprint
import code
import os

from clustering_cores.core_classroom_analysis.core_classroom_analysis import core_classroom_analysis

def main_online_users_TS_analysis():
    parser = argparse.ArgumentParser(description='Online user weblog time series analysis originally designed for nanoHUB.org')
    
    ### (OPTIONAL)
    parser.add_argument('--scratch_dir', help='location of scratch directory for temporary files', 
                                         action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))
                                    
    ### internal options
    parser.add_argument('--CI', help='start GitLab CI pipeline', 
                                action='store_true')
    parser.add_argument('--CI_dir', help='location of CI directory', 
                                    action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI'))
                                    
    inparams = parser.parse_args()       
    
    ### TODO summarize input options
    pprint(inparams)
    
    ### Analysis: classroom detection
                    
    # prepare data
    
    # classroom detection
    core_classroom_analysis(inparams)
                            
if __name__ == '__main__':
    main_online_users_TS_analysis() 
