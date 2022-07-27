# Classroom Clustering Guide

### Step 1: Run clustering algorithm on db2

Open terminal, then

`ssh username@db2.nanohub.org`

`cd xufeng-clustering`

If want to run Xufeng's algorithm:
~~~~
python3 main_online_users_TS_analysis.py --SQL_username username_ro --SQL_password abcdefghij --class_probe_range YYYY-MM-DD:YYYY-MM-DD
~~~~

If want to run Mike's algorithm:
~~~~
python3 main_online_users_TS_analysis.py --SQL_username username_ro --SQL_password abcdefghij --class_probe_range YYYY-MM-DD:YYYY-MM-DD --task cost_cluster_analysis
~~~~