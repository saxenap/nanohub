import os
from main_online_users_TS import main_online_users_TS

def run_clustering(task, firstyear, lastyear, bucketname, objectpath, loglevel):
    firstyear = firstyear + "-01-01" #semester 1
    lastyear = lastyear + "-07-02" #semester 2
    if bucketname == '':
        bucketname = 'nanohub.processed'
    if objectpath == '':
        objectpath = 'clusters/${' + task + '}/by_semester'
    if loglevel == '':
        loglevel = 'INFO'

    cmd1 = os.system("python3 main_online_users_TS.py "
                     "--cost_probe_range " + firstyear + ":" + lastyear + " "
                     "--class_probe_range " + firstyear + ":" + lastyear + " "
                     "--task $(" + task + ") "
                     "--bucket_name $(" + bucketname + ") "
                     "--object_path $(" + objectpath + ") "
                     "--log_level $(" + loglevel + ") "
                     "(other_flags)")




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
    run_clustering('mike', '2006', '2006', '', '', '')