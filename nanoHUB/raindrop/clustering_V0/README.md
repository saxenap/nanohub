# Xufeng-Clustering Contents

## Overview
This repository performs two high level functions.
1. It performs the user clustering into groups based on their behavior on Nanohub (i.e., tool usage statistics) and their geoip.
2. With that result obtain, it subsequently pushes it onto wang159.myremekes on DB2. 

Afterwards, the nightly cronjobs will extract the data from DB2, utilize the grouping, extract tools/logs, and upload the results to SalesForce.

## Detailed Breakdown (file-by-file)
* CI/data: Original gitlab pipeline's local data storage (contains past toolstart usage logs from 1-1-2018 to 5-1-2018 as .feather files) allows debugging clustering algorithms without connection to db2.
* core_classroom_detection: performs (i) the classification of users into clusters based on geoip, toolusage, email domains, and gaussian time window, and (ii) combines clusters into single clusters (this is the first post-processing filter, the second one is a jupyter notebook on the nanohub_salesforce_integ repo. See: https://github.com/wang2506/nanohub_salesforce_integ).
* core_quick_cluster_detection: Mike Zentner's original clustering methodology (deprecated). May contain overlap and/or novelties different from Xufeng's method.
* data: geoip table by maxmind.
* preprocessing: builds an engine to connect from current machine to DB2 and extracts the desired data based on dates, which are in turn specified by the user in main_online_users_TS_analysis.py. 
* temp: backup data - allows for the clustering code to be run for debugging purposes without reloading the data from DB2.
* clr_to_db2.py: mechanism to transfer clustered results (which are in /temp/cp1_detected_clusters_df.pkl) to wang159.myremekes on DB2. 
* main_online_users_TS_analysis.py: the clustering algorithm allows the user to specify the classroom details (i.e., what counts as a class/group?), as well as the date ranges of interest.






