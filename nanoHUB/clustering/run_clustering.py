import os
from dataclasses import dataclass, field
from main_online_users_TS_analysis import main_online_users_TS_analysis

@dataclass
class ClusteringFlags:
    #general
    task: str
    firstYear: str
    lastYear: str
    class_probe_range: str = field(default = firstYear + "-01-01" + ":" + lastYear  + "-07-02") #check

    #data
    geoip2_mmdb_filepath: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'data', 'GeoLite2-City.mmdb')) #check

    #directories
    outputDir: str = field(default = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'output')) #check
    scratchDir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp'))  #check
    namePrefix: str = field(default='users_analysis')
    displayOutput: bool = field(default='True')
    noSaveOutput: bool = field(default='False')
    saveToGeddes: bool = field(default='False')
    bucketName: str = field(default='nanohub.processed')
    objectPath: str = field(default='clusters/${' + task + '}/by_semester')

    #classroom detection behavior (xufeng)
    classActivityTol: str = field(default='2')
    classAttentionSpan: str = field(default='3')
    classSizeMin: str = field(default='5')
    classDistanceThreshold: str = field(default ='50')
    classMergeTimeThreshold: str = field(default='120')
    classMergeDistanceThreshold: str = field(default='5')

    #quick cost-based cluster analysis
    costSizeMin: str = field(default='4')
    costForceAllDiffLvl: str = field(default='501')
    costTolerance: str = field(default='57')

    #dask
    daskScheduler: str = field(default='single-threaded')

    #internal options
    CI: str = field(default='False') #check
    CI_dir: str = field(default=os.path.join(os.path.dirname(os.path.realpath(__file__)), 'CI')) #FILL
    generateNotebookCheckpoints: str = field(default='True')
    gatherDataOnly: bool = field(default='False') #check
    useOldData: bool = field(default='False') #check
    logLevel: str = field(default='INFO')

def run_clustering(flags):
    flags.firstYear = flags.firstYear + "-01-01" #semester 1
    flags.lastYear = flags.lastYear + "-07-02" #semester 2

    final_df = main_online_users_TS_analysis(flags)
    print(final_df)



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
    run_clustering(ClusteringFlags())