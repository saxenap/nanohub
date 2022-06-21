import os
from dataclasses import dataclass, field
from datetime import datetime, date

from main_online_users_TS_analysis import main_online_users_TS_analysis
from datetime import datetime

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
        

def run_clustering(flags):

    startCheck = datetime.strptime(flags.startDate, '%Y-%m-%d')
    endCheck = datetime.strptime(flags.endDate, '%Y-%m-%d')

    if not startCheck < endCheck:
        raise Exception("startDate before endDate")

    final_df = main_online_users_TS_analysis(flags)
    return final_df


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