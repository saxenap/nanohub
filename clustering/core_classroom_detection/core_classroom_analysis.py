from pprint import pprint
import logging
import pandas as pd
import os

import geoip2.database

from dask import dataframe as dd
from dask.multiprocessing import get
from dask.diagnostics import ProgressBar

import numpy as np
import datetime

from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances

import shelve
import pickle

import code

def prepare_data(inparams):
    
    #
    # Load dataframes in feathers
    #
    
    logging.info('Loading relevent data ...')
    
    toolstart_df = pd.read_feather(os.path.join(inparams.scratch_dir, 'toolstart.feather'))
    toolstart_df['tool'] = toolstart_df['tool'].apply(lambda x: x.lower())

    jos_tool_version = pd.read_feather(os.path.join(inparams.scratch_dir, 'jos_tool_version.feather'))

    jos_users = pd.read_feather(os.path.join(inparams.scratch_dir, 'jos_users.feather'))
    
    # Translate toolname+toolversion (pntoy_r123) into just toolname (pntoy). 
    # In addition, for any toolname+toolversion not found in jos_tool_version table, treat it as toolname.
    toolrun_df = toolstart_df.join(jos_tool_version[['instance', 'toolname']].set_index('instance'), on='tool')
    
    # for toolnames that cannot be found in table "jos_tool_version", use tool instead
    toolrun_df['toolname']=toolrun_df['toolname'].fillna(toolrun_df['tool'])

    # remove all rows with protocol != 5,6,7
    toolrun_df = toolrun_df[toolrun_df['protocol'].isin([5,6,7])]

    # remove several user that are not actual person
    toolrun_df = toolrun_df[toolrun_df.user != 'instanton']

    # convert datetime to date only
    toolrun_df['date'] = toolrun_df['datetime'].dt.floor('D')

    # remove column 'tool', 'datetime', and 'protocol'. They are not used anymore
    toolrun_df = toolrun_df.drop(columns=['tool','protocol','datetime'])
    
    # drop duplicate rows
    toolrun_df.drop_duplicates(inplace=True)
    
    #
    # Load geospatial data
    #
            
    def get_geo_data(ip):
        try:
            reader = geoip2.database.Reader(inparams.geoip2_mmdb_filepath)
            response = reader.city(ip)
            return [response.location.longitude, response.location.latitude]
                    
        except:
            return [None, None]
            
    pbar = ProgressBar()
    pbar.register()
    geo_data = dd.from_pandas(toolrun_df['ip'], npartitions=200) \
              .map_partitions(lambda df: df.apply(get_geo_data)) \
              .compute(scheduler=inparams.dask_scheduler);

    lon_lat = np.stack(geo_data.values)
    toolrun_df['lon'] = lon_lat[:,0].astype(np.float)
    toolrun_df['lat'] = lon_lat[:,1].astype(np.float)
    
    logging.info('Longitude and Latitude assigned user tool run activities')
    logging.info('(toolrun_df)')
    logging.info(toolrun_df)
    
    return (toolrun_df, toolstart_df, jos_users, jos_tool_version)



def form_activity_blocks(user_df, activity_tol):
    # given a user's DF, form activity blocks for each of the tool
    user_tools = user_df['toolname'].unique()
    
    activity_blocks = list()
        
    for this_tool in user_tools:
        # tools from each user, sort from latest to earliest
        tooluse_df = user_df[user_df.toolname == this_tool].sort_values('date',ascending=False)

        # start from latest date (present)
        start_date = tooluse_df.iloc[0]['date']
        end_date = tooluse_df.iloc[0]['date']
        ip_set = set([tooluse_df.iloc[0]['ip']])
               
        for index, this_row in tooluse_df.iterrows():
            # for each date (moving backward in time)
            this_date = this_row['date']
            if (start_date - this_date) > activity_tol:
                # this time has moved out of activity tolerance range
                # close previous activity block and start a new one
                for this_ip in ip_set:
                    activity_blocks.append([this_tool, \
                                            start_date - activity_tol, \
                                            end_date + activity_tol, \
                                            this_ip])
                    
                ip_set = set()
                
                end_date = this_date

            # update start_date
            start_date = this_date
            ip_set.add(this_row['ip'])
            
        # insert the last block
        for this_ip in ip_set:
            activity_blocks.append([this_tool, \
                                    start_date - activity_tol, \
                                    end_date + activity_tol, \
                                    this_ip])
        
    # add username to dataframe
    #activity_blocks['user'] = user_df.user.unique()
    
    return pd.DataFrame(activity_blocks, columns=['tool', 'start', 'end', 'ip'])




# great circle distance
def haversine_metric(x,y):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """

    # convert decimal degrees to radians 
    # lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    lon1 = np.radians(x[0])
    lat1 = np.radians(x[1])
    lon2 = np.radians(y[0])
    lat2 = np.radians(y[1])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a)) 
    r = 6371 # Radius of earth in miles. Use 6371 for kilometers
    return c * r

def haversine_affinity(X):
    return pairwise_distances(X, metric=haversine_metric)




def geospatial_cluster(cluster_input, cluster_size_cutoff, class_distance_threshold):
    """
    Given individual user's activity blocks for all users, all days, use geospatial clustering
    to form clusters with certrain intra-cluster distance limit.
    """
    date_earliest = cluster_input.start.min()
    date_latest =  cluster_input.end.max()
    #logging.info('Date range: '+str(date_earliest)+' - '+str(date_latest))

    cluster_output = list()
    cluster_input['cluster']=None
    cluster_input['scanned_date']=datetime.datetime(1900,1,1)

    cluster_output_np = np.empty((0,len(cluster_input.columns)))

    for this_date in [date_earliest + datetime.timedelta(days=n) for n in range(0, int((date_latest-date_earliest).days+1))]:

        # for each date spanned by cluster_input
        
        this_date_all_blocks = cluster_input[(cluster_input.start<=this_date) & (cluster_input.end>=this_date)]

        this_date_all_tools = this_date_all_blocks.tool.unique()
        
        for this_tool in this_date_all_tools:
            this_date_cluster_input = this_date_all_blocks[this_date_all_blocks.tool == this_tool]
            
            # if sample too small, skip
            if len(this_date_cluster_input.index) < cluster_size_cutoff:
                continue
            
            # number of users for this tool is large enough, globally, to warrent a geospatial clustering
            this_clustering = AgglomerativeClustering(affinity=haversine_affinity, \
                                                 linkage='average', \
                                                 n_clusters = None, \
                                                 distance_threshold = class_distance_threshold \
                                                ).fit(this_date_cluster_input[['lon','lat']].values)

            cluster_input.loc[this_date_cluster_input.index, 'cluster'] = this_clustering.labels_
            cluster_input.loc[this_date_cluster_input.index, 'scanned_date'] = this_date

            # add this tool run's scanned_date, tool, user into dict
            cluster_output_np = np.append(cluster_output_np, cluster_input.loc[this_date_cluster_input.index].to_numpy(), axis=0)

    return cluster_output_np




def form_cluster_blocks(tool_clusters_df):
    '''
    Given a tool's clusters from all users, join neighboring clusters that
    shares one or more common users
    '''
    
    all_scanned_dates = np.sort(tool_clusters_df['scanned_date'].unique())
    
    # list of dict [{'tool': 'pntoy', 'start':datetime, 'end':datetime, users': list()}, .....]
    all_clusters = list()
    
    if len(all_scanned_dates) > 0:
        last_update_date = all_scanned_dates[0]
    
    for index, this_date in enumerate(all_scanned_dates):
        # for each scanned date
        clusters_in_this_date = tool_clusters_df[tool_clusters_df.scanned_date == this_date]

        cluster_ids = clusters_in_this_date['cluster'].unique()
        
        for this_cluster_id in cluster_ids:
            # for each cluster ID
            this_cluster_df = clusters_in_this_date[clusters_in_this_date.cluster == this_cluster_id]
            
            # see if it can be aggregated with one of the candidates clusters
            this_all_users = set(this_cluster_df.user)
            cluster_matched = False
            
            for this_candidate in all_clusters:
                if index > 0:
                    if this_candidate['last_update'] != all_scanned_dates[index-1]:
                        # only append to clusters that is active in previous, adjacent date
                        continue
                
                this_candidate_users = tool_clusters_df.loc[this_candidate['users_row_id']]['user']
                if this_all_users & set(this_candidate_users):                    
                    # match
                    this_candidate['last_update'] = this_date
                    this_candidate['users_row_id'] = this_candidate['users_row_id'].append(this_cluster_df.index)
                    
                    cluster_matched = True
                    break
            
            if not cluster_matched:
                # no match found, insert this cluster as new into all_candidates_clusters
                all_clusters.append({'last_update':this_date, 'users_row_id':this_cluster_df.index})
                #display('adding '+str(len(this_cluster_df.index))+' rows')

    
    # turn into a dataframe
    all_clusters_df = pd.DataFrame(all_clusters)
    all_clusters_df.drop('last_update',axis=1,inplace=True)
    
    # find the earliest start and latest end of all users within cluster
    all_clusters_df['start'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].start.min(), axis=1)
    all_clusters_df['end'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].end.max(), axis=1)
    
    # find number of users involved in this detected super cluster
    all_clusters_df['user_count'] = all_clusters_df.apply(lambda x: len(tool_clusters_df.loc[x.users_row_id].user.unique()), axis=1)
    
    # find the average coordinate
    try:
        # avoid a DASK bug
        all_clusters_df['mean_lat'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].lat.mean(), axis=1)
        all_clusters_df['mean_lon'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].lon.mean(), axis=1)
    except:
        all_clusters_df['mean_lat'] = all_clusters_df.apply(lambda x: None, axis=1)
        all_clusters_df['mean_lon'] = all_clusters_df.apply(lambda x: None, axis=1)
        
    all_clusters_df['lat_lon'] = all_clusters_df.apply(lambda x: list(zip(tool_clusters_df.loc[x.users_row_id].lat.values, tool_clusters_df.loc[x.users_row_id].lon.values)), axis=1)
    
    return all_clusters_df



def core_classroom_analysis(inparams):

    logging.info('Conducting Classroom Analysis ...')

    #
    # Load dataframes in feathers
    #
    
    (toolrun_df, toolstart_df, jos_users, jos_tool_version) = prepare_data(inparams)

    # Limit analysis range to within limits
    
    if inparams.class_probe_range == 'latest':
        # probes only the latest (today - 2 STD of Gaussian attention window function)
        # Each user simulation run action is expanded to 1 STD, and therefore the resulting cluster has max width of 2 STD
        data_probe_range = [datetime.date.today()-datetime.timedelta(days=inparams.class_attention_span*2), datetime.date.today()]
        
    else:
        # probes given time range
        # expects inparams.class_probe_range in form of, for example, '2018-1-1:2018-5-1'
        datetime_range_list = inparams.class_probe_range.split(':')
        data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in datetime_range_list] 
        
    logging.info('Probing range: '+data_probe_range[0].strftime('%Y-%m-%d')+' - '+data_probe_range[1].strftime('%Y-%m-%d')) 
       
    #
    # Form user tool activity blocks
    #
    activity_tol = datetime.timedelta(days=inparams.class_activity_tol)
    ddata = dd.from_pandas(toolrun_df, npartitions=200) \
              .groupby('user').apply(form_activity_blocks, activity_tol = activity_tol) \
              .compute(scheduler=inparams.dask_scheduler)
    user_activity_blocks_df = ddata[(ddata.start>=data_probe_range[0]) &(ddata.end<=data_probe_range[1])] \
                                    .reset_index().drop(['level_1'], axis=1)
    
    #
    # Geospatial clustering
    #
    
    # join the IP and Lat, Lon
    user_activity_blocks_df = pd.merge(user_activity_blocks_df, toolrun_df[['ip','lon','lat']].drop_duplicates(), on='ip', how='left')

    # remove all NaN entries in Lat and Lon
    user_activity_blocks_df = user_activity_blocks_df[~user_activity_blocks_df.lat.isna() & ~user_activity_blocks_df.lon.isna()]

    logging.info('Tool usage activity blocks formed for each user for all days')
    logging.info('(user_activity_blocks_df)')
    logging.info(user_activity_blocks_df)
        
    # Geospatial clustering for each day, each tool
    ddata = dd.from_pandas(user_activity_blocks_df, npartitions=200) \
            .groupby('tool')\
            .apply(geospatial_cluster, \
                   cluster_size_cutoff=inparams.class_size_min, \
                   class_distance_threshold=inparams.class_distance_threshold) \
            .compute(scheduler=inparams.dask_scheduler)

    detected_clusters_df = pd.DataFrame(np.vstack(ddata.to_numpy()), columns=(user_activity_blocks_df.columns.to_list()+['cluster', 'scanned_date']))

    # remove duplicated: same user, same tool, appearing in the same cluster more than once
    cluster_output_nodup = detected_clusters_df.drop_duplicates(subset=['scanned_date', 'cluster', 'user','tool'])

    passed_cutoff = cluster_output_nodup[['scanned_date','cluster','tool','user']]
    passed_cutoff = passed_cutoff.groupby(['scanned_date','cluster','tool']).count()['user'] > inparams.class_size_min
    
    cluster_output_candidate = cluster_output_nodup.join(passed_cutoff, on=['scanned_date', 'cluster', 'tool'], rsuffix='_meet_class_size_min')
    cluster_output_candidate['user_meet_class_size_min'].fillna(False, inplace=True)
    cluster_output_candidate = cluster_output_candidate[cluster_output_candidate.user_meet_class_size_min]

    logging.info('Geospatially clustered candidates for classrooms on each day:')
    logging.info('(cluster_output_candidate)')
    logging.info(cluster_output_candidate)

    # Aggregate clusters in neighboring days into one
    code.interact(local=locals())
    ddata = dd.from_pandas(cluster_output_candidate, npartitions=60) \
              .groupby('tool').apply(form_cluster_blocks) \
              .compute(scheduler=inparams.dask_scheduler)
    #'end', 'mean_lat', 'mean_lon', 'start', 'user_count', 'users_row_id'
    class_cluster_candidate = ddata.reset_index()
    logging.info('Class candidates formed for each user for all days')
    logging.info('(class_cluster_candidate)')
    logging.info(class_cluster_candidate)

    # NOTEBOOK CHECKPOINT
    if inparams.generate_notebook_checkpoints:
        logging.info('Generating Jupyter Notebook checkpoint 1: Synchrony EDA')
        
        class_cluster_candidate.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_class_cluster_candidate.pkl'))
        user_activity_blocks_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_user_activity_blocks_df.pkl'))        
        detected_clusters_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_detected_clusters_df.pkl'))        
        jos_users.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_jos_users.pkl'))        
        toolrun_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_toolrun_df.pkl'))
        cluster_output_candidate.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_cluster_output_candidate.pkl'))
                       
        with open(os.path.join(inparams.scratch_dir, 'core_classroom_analysis_cp1.pkl'), 'wb') as f:
            pickle.dump([inparams],f)


