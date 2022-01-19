# -*- coding: utf-8 -*-
"""
Created on Wed Sep 30 15:24:06 2020

@author: henry
"""
import pandas as pd
import numpy as np
import os
import pickle as pk

## take in the classroom detection outputs, filter them and push them onto DB2

# %% import the results of the classroom detection algorithm


from nanoHUB.application import Application

application = Application.get_instance()
wang159_myrmekes_db = application.new_db_engine('wang159_myrmekes')

cwd = os.getcwd()
dir_data = cwd+'/temp/'

# classtool - need to re-number the classids from classtool
with open(dir_data+'cp1_classtool_info_df.pkl','rb') as f:
    cluster_classtool_info = pk.load(f)

print(cluster_classtool_info.head(2))

# class info - append this to wang159myrmekes database and renumber the classids
with open(dir_data+'cp1_class_info_df.pkl','rb') as f:
    cluster_class_info = pk.load(f)
    
print(cluster_class_info.head(2))

# student info
with open(dir_data+'cp1_students_info_df.pkl','rb') as f:
    cluster_students_info = pk.load(f)

print(cluster_students_info.head(2))

# %% get DB2 access, find what classid to start at, renumber class ids, then add to DB2 table

# obtain classid from DB2

class_info_df = pd.read_sql_query('select class_id from cluster_class_info order by '+\
                                  'class_id desc limit 100', wang159_myrmekes_db)
cid_start = class_info_df['class_id'][0]+1

# start stop class_id (and indexes) recalculation
cid_start =  class_info_df['class_id'][0]+1
cid_end = cid_start + cluster_class_info.shape[0]
cluster_class_info['class_id'] = range(cid_start,cid_end)

cid_track = cid_start
for index,val in enumerate(cluster_class_info['class_id'].to_list()):
    #find all the row indexes that have classid equal to index
    
    #cluster_classtool_info
    cluster_classtool_info['class_id'][cluster_classtool_info['class_id']==index] = val
    cluster_students_info['class_id'][cluster_students_info['class_id']==index] = val

# add to DB2 table
cluster_class_info = cluster_class_info.drop(columns='ip_set')
cluster_class_info.to_sql('cluster_class_info', con=wang159_myrmekes_db, if_exists='append', chunksize=20000)
cluster_classtool_info.to_sql('cluster_classtool_info', con=wang159_myrmekes_db, if_exists='append', chunksize=20000)
cluster_students_info.to_sql('cluster_students_info',con=wang159_myrmekes_db,if_exists='append',chunksize=20000)







