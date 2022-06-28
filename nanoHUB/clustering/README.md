## this directory has the "production clustering" algrithms
## need to integrate the reaindrop 

## Mike algorithm is in core_quick_cluster_detection
## Xufeng algortihm is in core_classroom_detection

---
# run_clustering.py usage:

This file is for running clustering for a specific time, all time,
or with a variety of options.

**command object = ExecuteAlgorithmCommand object

## Different ways to cluster

1. Cluster for all
   1. TwoSemesterTimeFrameGenerator.cluster_for_all()
2. Cluster from [start] to [end]
   1. TwoSemesterTimeFrameGenerator.cluster_for_start_end()
3. Cluster with special options
   1. Build a command object
   2. Pass to run_clustering

### ExecuteAlgorithmCommand Class
This class contains all options for running clustering. A detailed description
of each can be found in **main_online_users_TS**. This object must be created and passed into the **run_clustering**
function, which will then return a dataframe of the clusters for that time period.

All the other functions/classes in this file are related to building the command object and passing it
to be ran by run_clustering in some way.

### TwoSemesterTimeFrameGenerator Class
This class contains all functions for clustering that split data in a two semester format.

**cluster_for_all**: This function will return a list of dataframes for all
time until the present since the start of nanoHUB (2006, 1, 1).

**cluster_for_start_end**: This function will return a list of dataframes
for all time in between the passed times for the passed algorithm.

create_timeframe_list: Creates a list of time periods to be made into command objects.
Necessary for mpire.

timeframe_to_str: Converts timeframe list into strings, command object must be created with strings.

timeframe_to_command: Converts the timeframe list into command objects, to be passed into run_clustering.
Necessary for mpire.

## cluster_by_command Function
Clusters using nested pool multiprocessing (mpire). Due to how mpire works, a list of command objects must be passed.
Used by both cluster_for_all and cluster_for_start_end.

n_jobs=None -> uses max cores

**For custom clustering options**: Unfortunately if you want to use multiprocessing with custom options, you will have to build each command object yourself.
If you don't want to do this, either use the Makefile to cluster with options and multiprocessing, or just go one "semester" at
a time and create a command object (ExecuteAlgorithmCommand object), and then pass it directly into run_clustering. If it is passed
into cluster_by_command, multiprocessing will be used, however most options will be broken due to the handler not being used).


---

Things to fix:

In combine_clusters.py, the multiprocessing is done with the built-in Python multiprocessing.
It just errors for some reason when using mpire there.

There is an instance of nested multiprocessing, inside core_classroom_analysis on line 102. If this is
fixed delete daemon=False parameter from the call in cluster_by_command.

Maximum cores used set to 10 right now. This is because the ssh requests cannot handle it.