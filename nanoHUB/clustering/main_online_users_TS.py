import argparse
import os
import time
from run_clustering import run_clustering

def main_online_users_TS():
    parser = argparse.ArgumentParser(
        description='Online user weblog time series analysis originally designed for nanoHUB.org')

    # task options
    parser.add_argument('--task', help='specific task',
                        action='store', default='core_classroom_analysis')

    # data
    parser.add_argument('--geoip2_mmdb_filepath', help='full file path of mmdb file from GeoIP2',
                        action='store',
                        default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb'))

    # directories
    parser.add_argument('--output_dir', help='location of output directory for output files',
                        action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output'))
    parser.add_argument('--scratch_dir', help='location of scratch directory for temporary files',
                        action='store', default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))
    parser.add_argument('--name_prefix', help='prefix to all output files',
                        action='store', default='users_analysis')

    parser.add_argument('--display_output', dest='display_output', help='should display/return/print output',
                        action='store_true', default=True)

    parser.add_argument('--no_save_output', dest='no_save_output', help='should not save output file locally',
                        action='store_true', default=False)

    parser.add_argument('--save_to_geddes', dest='save_to_geddes',
                        help='should save resulting csv to data lake in geddes',
                        action='store_true')

    parser.add_argument('--no-save_to_geddes', dest='save_to_geddes',
                        help='should not save resulting csv to data lake in geddes',
                        action='store_false')

    parser.add_argument('--bucket_name', help='bucket name in Geddes', action='store')
    parser.add_argument('--object_path', help='object path inside the bucket in Geddes', action='store', default='')

    parser.set_defaults(save_to_geddes=False)

    # class room detection behavior
    parser.add_argument('--class_probe_range',
                        help='classroom detection: date range of the class to be analyzed. For example, 2018-1-1:2018-5-1',
                        action='store', default='latest')  # '2020-9-25:2020-10-13')
    parser.add_argument('--class_activity_tol',
                        help='classroom detection: minimal days apart to declare two use of same tool as separate activity blocks',
                        action='store', default=2)
    parser.add_argument('--class_attention_span',
                        help='classroom detection: the standard deviation of gaussian shaped attention window function',
                        action='store', default=3)
    parser.add_argument('--class_size_min',
                        help='classroom detection: minimal number of users within a cluster to declare it as a valid class',
                        action='store', default=5)
    parser.add_argument('--class_distance_threshold',
                        help='classroom detection: maximum intra-cluster distance in km for geospatial clusters',
                        action='store', default=50)
    parser.add_argument('--class_merge_time_threshold',
                        help='classroom detection: when merging similar clusters, maximum time range allowed for merging',
                        action='store', default=120)
    parser.add_argument('--class_merge_distance_threshold',
                        help='classroom detection: when merging similat cluster, maximum intra-cluster distance in km for geospatial clusters',
                        action='store', default=5)

    # quick cost-based cluster analysis
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
    parser.add_argument('--generate_notebook_checkpoints',
                        help='shelve variables in order to connect with notebooks at various points',
                        action='store_true')
    parser.add_argument('--use_old_data', help='use feature data from previous run',
                        action='store_true')

    parser.add_argument('--gather_data_only', help='exit after gather data without analysing clusters',
                        action='store_true')

    parser.add_argument('--log_level', help='logging level (INFO, DEBUG etc)',
                        action='store', default='INFO')


    inparams = parser.parse_args()

    # redefine inparams for cronjob smoothness - since we use this setting anyway
    inparams.generate_notebook_checkpoints = True  # so outputs are saved

    inparams.class_probe_range = inparams.class_probe_range.replace('_', ':')

    returned_cluster_df = run_clustering(inparams)
    print(returned_cluster_df)



if __name__ == '__main__':
    start = time.time()
    main_online_users_TS()
    end = time.time()
    print("Time:", end - start)
