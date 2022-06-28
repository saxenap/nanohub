import multiprocessing
from pprint import pprint
import pandas as pd
import numpy as np
import datetime

from scipy.sparse import coo_matrix

from sklearn.metrics import pairwise_distances
from sklearn.cluster import AgglomerativeClustering, DBSCAN

from dask import dataframe as dd
from dask.multiprocessing import get
from dask.diagnostics import ProgressBar

pbar = ProgressBar()
pbar.register()


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
    
    
    
    
def user_to_group_clusters(user_group, min_size):
    '''
    Form a group clusters from individual user activity blocks
    '''
    
    # remove group clusters that are smaller than minimal size
    if user_group.shape[0] < min_size:
        return None
    
    user_set = user_group.user.unique()
    ip_set = user_group.ip.unique()
    mean_lon = user_group.lon.mean()
    mean_lat = user_group.lat.mean()

    return pd.DataFrame([[set(user_set), set(ip_set), mean_lon, mean_lat]], columns=['user_set', 'ip_set', 'mean_lon', 'mean_lat'])
    
    


def find_mergable_clusters(this_merged_user_set, this_user_set):
    '''
    Given each merged cluster from previous day, find if there is any
    clusters that can be merged on this day
    '''    
    #display(this_merged_user_set)
    #display(this_user_set)
    
    common_set = this_user_set.intersection(this_merged_user_set)
    
    
    merged_size = len(this_merged_user_set)
    this_size = len(this_user_set)
    common_size = len(common_set)
    
    if merged_size*this_size*common_size == 0:
        # if any of these is empty, do not merge
        return 0
    
    # see if this common_set is at least 80% of the smaller set
    if merged_size >= this_size:
        share_ratio = common_size/this_size
    else:
        share_ratio = common_size/merged_size
    
    return share_ratio




def intra_tool_cluster_annex(one_tool_clusters):
    '''
    Joining clusters togethers if they:
    1. adjacent in time
    2. of same tool (one_tool_clusters only contains 1 tool anyway)
    3. shares 80% of same users at least by one cluster 
    '''
    
    # create empty df for merged clusters
    merged_tool_clusters = pd.DataFrame(columns=['start', 'end', 'mean_lon', 'mean_lat', 'user_set', 'ip_set'])
    
    # time range the cluster covered
    start_date = one_tool_clusters[1].scanned_date.min()
    end_date = one_tool_clusters[1].scanned_date.max()
    
    date_list = [start_date + datetime.timedelta(days=x) for x in range(0, (end_date-start_date).days)]
    
    # begin to annex clusters day by day
    for this_date in date_list:
        # for each date
        
        # tool, date
        this_date_clusters = one_tool_clusters[1][one_tool_clusters[1].scanned_date == this_date]
        
        # tool, date, cluster, DBSCAN uniquely identifies a cluster
        
        # mergable clusters on this date
        this_date_merged_tool_clusters = merged_tool_clusters[merged_tool_clusters.end == (this_date-datetime.timedelta(days=1))]
        
        # iterate over this_date_clusters, and 
        # 1. merge the mergable clusters with merged_tool_clusters
        # 2. append the new clusters if not mergable
        for row in this_date_clusters.itertuples():        
            this_user_set = row.user_set
            result = this_date_merged_tool_clusters.user_set.apply(find_mergable_clusters, this_user_set = this_user_set)
            
            # find the results above the cutoff. Should only have 1
            to_merge = False
            if not result.empty:
                # some scores are found
                max_score_index = result.idxmax()
            
                if result[max_score_index] >= 0.5:
                    # maximum similiarty exceeds threshold                    
                    to_merge = True
    
            if to_merge:
                # merge
                
                merged_user_total = len(merged_tool_clusters.loc[max_score_index].user_set)
                this_user_total = len(row.user_set)
                
                merged_tool_clusters.at[max_score_index, 'end'] = row.scanned_date  
                
                merged_tool_clusters.at[max_score_index, 'mean_lon'] = \
                    (row.mean_lon*this_user_total + merged_tool_clusters.loc[max_score_index].mean_lon*merged_user_total) \
                    / (this_user_total + merged_user_total)
                
                merged_tool_clusters.at[max_score_index, 'mean_lat'] = \
                    (row.mean_lat*this_user_total + merged_tool_clusters.loc[max_score_index].mean_lat*merged_user_total) \
                    / (this_user_total + merged_user_total)
                
                merged_tool_clusters.at[max_score_index, 'user_set'] = \
                    merged_tool_clusters.loc[max_score_index].user_set.union(row.user_set)
                    
                merged_tool_clusters.at[max_score_index, 'ip_set'] = \
                    merged_tool_clusters.loc[max_score_index].ip_set.union(row.ip_set)
                
            else:

                merged_tool_clusters = merged_tool_clusters.append({ \
                                                        'start':    row.scanned_date, \
                                                        'end':      row.scanned_date, \
                                                        'mean_lon': row.mean_lon, \
                                                        'mean_lat': row.mean_lat, \
                                                        'user_set': row.user_set, \
                                                        'ip_set':   row.ip_set \
                                                        }, ignore_index=True)

                # merged_tool_clusters = pd.concat([
                #     merged_tool_clusters, {
                #     'start':    row.scanned_date,
                #     'end':      row.scanned_date,
                #     'mean_lon': row.mean_lon,
                #     'mean_lat': row.mean_lat,
                #     'user_set': row.user_set,
                #     'ip_set':   row.ip_set
                #     }],
                #     axis=0,
                #     join='outer',
                #     ignore_index=True
                # )
  
    return merged_tool_clusters
    
    


def find_inter_mergable_clusters(this_row, intra_tool_cluster_df, time_tolerance, dist_tolerance):
    # iterate through entire intra_tool_cluster_df
    
    eligible_clusters = intra_tool_cluster_df

<<<<<<< HEAD
=======
    #convert to datetime, causes issue if not converted
    eligible_clusters['start'] = pd.to_datetime(eligible_clusters['start'])
    eligible_clusters['end'] = pd.to_datetime(eligible_clusters['end'])
    
>>>>>>> d497d3e594f63cbc68dc01775014e89583e6b6de
    # filter dates
    eligible_clusters = eligible_clusters[(abs(eligible_clusters.start - this_row.end) <= time_tolerance) | \
                                          (abs(eligible_clusters.end - this_row.start) <= time_tolerance)]
    
    # filter geo-location
    distance = eligible_clusters\
                .apply(lambda x: haversine_metric([x.mean_lon, x.mean_lat],\
                                                  [this_row.mean_lon, this_row.mean_lat]), \
                       axis=1)    
    eligible_clusters = eligible_clusters[distance < dist_tolerance]

    # form similarity matrix by number of users shared across
    # shared_user is a percentage (0-1). 
    shared_user = eligible_clusters.user_set\
                    .apply(lambda x: len(this_row.user_set.intersection(x))/len(this_row.user_set.union(x)))
    
    row_index = np.ones(len(shared_user.index))*int(this_row.name)
    
    return np.array([shared_user.values, row_index, shared_user.index.values])
        



def combine_clusters(inparams, cluster_post_sychrony):

    # transform individual user's clusters into group cluster identified by scanned_date, tool, cluster, and DBSCAN
    group_clusters = cluster_post_sychrony.groupby(['tool', 'cluster', 'scanned_date','DBSCAN']) \
                                          .apply(user_to_group_clusters, min_size=inparams.class_size_min) \
                                          .reset_index()

    #
    # First, annex clusters adjacent in time within the same tool group to form intra-tool clusters
    #

    grouped = group_clusters.groupby('tool')
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        intra_tool_cluster_df = pool.map(intra_tool_cluster_annex, [(name, group) for name, group in grouped])
    intra_tool_cluster_df = pd.concat(intra_tool_cluster_df)
    intra_tool_cluster_df.index.name = 'tool'

    #                      
    # Second, annex clusters sharing same users within a time range to form final classes
    #
    
    intra_tool_cluster_df = intra_tool_cluster_df.reset_index()

    # generate similiarity matrix based on number of users shared. 
    # hard rules are also in place for cases that should not be merged
    similarity_tuples = intra_tool_cluster_df.apply(find_inter_mergable_clusters, \
                                            intra_tool_cluster_df = intra_tool_cluster_df, \
                                            time_tolerance = datetime.timedelta(days = inparams.class_merge_time_threshold), \
                                            dist_tolerance = inparams.class_merge_distance_threshold, \
                                            axis=1)

    similarity_tuples_hstack = np.hstack(similarity_tuples)

    similarity_matrix = coo_matrix( \
                             (similarity_tuples_hstack[0,:].astype(np.float32), \
                             (similarity_tuples_hstack[1,:].astype(int), \
                              similarity_tuples_hstack[2,:].astype(int)) \
                             )).toarray()
    # for some reason, float16 does not work (https://github.com/scipy/scipy/issues/7408)

    # clustering using DBSCAN with distance matrix
    cluster_result = DBSCAN(eps=5, min_samples=1, metric='precomputed').fit_predict(1/(similarity_matrix+0.0001))


    #
    # Output final classroom information
    #

    # total number of classes detected. Clusters start with index 0
    num_of_classes = cluster_result.max() + 1

    # output df templates
    students_info_df  = pd.DataFrame(columns=['user', 'class_id', 'parti_rate'])
    class_info_df     = pd.DataFrame(columns=['class_id', 'start', 'end', 'lon', 'lat', 'size', 'ip_set'])
    classtool_info_df = pd.DataFrame(columns=['toolname', 'class_id'])

    for this_class_index in range(0, num_of_classes):
        
        this_class_tool_clusters = intra_tool_cluster_df.loc[cluster_result == this_class_index]
        
        # student participation rate
        # this is how many sub-clusters each student appears in
        
        all_students_list = list()
        num_total_clusters = this_class_tool_clusters.shape[0]
        
        for this_user_set in this_class_tool_clusters.user_set:
            all_students_list.extend(list(this_user_set))
        
        this_students_df = pd.DataFrame(set(all_students_list), columns=['user'])
        
        this_students_df['class_id'] = this_class_index 
        this_students_df['parti_rate'] = this_students_df.user \
                                                .apply(lambda x: all_students_list.count(x)/num_total_clusters)
        
        
        students_info_df = students_info_df.append(this_students_df, ignore_index=True)
        
        # tool list
        
        this_classtool_df = pd.DataFrame(set(this_class_tool_clusters.tool), columns=['toolname'])
        this_classtool_df['class_id'] = this_class_index
        
        classtool_info_df = classtool_info_df.append(this_classtool_df, ignore_index=True)
        
        # class general information
        
        class_info_df = class_info_df.append({'class_id':this_class_index, \
                                              'start':this_class_tool_clusters.start.min(), \
                                              'end':this_class_tool_clusters.end.max(), \
                                              'lon':this_class_tool_clusters.mean_lon.mean(), \
                                              'lat':this_class_tool_clusters.mean_lat.mean(), \
                                              'ip_set':this_class_tool_clusters.ip_set.values, \
                                              'size':len(set(all_students_list))}, ignore_index=True)

        # class_info_df = pd.concat([class_info_df,
        #                           {'class_id':this_class_index,
        #                            'start':this_class_tool_clusters.start.min(),
        #                            'end':this_class_tool_clusters.end.max(),
        #                            'lon':this_class_tool_clusters.mean_lon.mean(),
        #                            'lat':this_class_tool_clusters.mean_lat.mean(),
        #                            'ip_set':this_class_tool_clusters.ip_set.values,
        #                            'size':len(set(all_students_list))}],
        #                             axis=0,
        #                             join='outer',
        #                             ignore_index=True
        #                           )
                                                
    return intra_tool_cluster_df, students_info_df, class_info_df, classtool_info_df
