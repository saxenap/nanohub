import code
from pprint import pprint
import pandas as pd
import numpy as np
import logging

import csv

from dask import dataframe as dd
from dask.multiprocessing import get
from dask.diagnostics import ProgressBar
pbar = ProgressBar()
pbar.register()



 
def user_cluster_formation(user_usage_row, user_usage_indexed_df, tolerance):
    
    others = user_usage_row.usages
    clusters = set()
    
    if len(others) == 0:
        # empty list
        return clusters
    
    clusterCandidates = set([user_usage_row.name])
    clusterDaySpan = user_usage_row.userDaySpans
    
    for clusteredUser, clusteredUserDistance in others:
        if clusteredUserDistance <= tolerance:
            # add all other usernames whose cost is lower than tolerance
            clusterCandidates.add(clusteredUser)
            
    for candidate in clusterCandidates:
        # iterate through all candidates that are closely associated with username #1
        if clusterDaySpan[0] == clusterDaySpan[1]:
            # username #1 only has a single-day activity
            clusterDay = clusterDaySpan[0]
            #candidateDaySpan = userDaySpans[candidate]

            candidateDaySpan = user_usage_indexed_df.loc[candidate].userDaySpans
                        
            if candidateDaySpan[0] <= clusterDay and candidateDaySpan[1] >= clusterDay:
                # single-day is within candidate activity span
                clusters.add(candidate)
                
            elif abs(candidateDaySpan[0] - clusterDay) == 1 or abs(candidateDaySpan[1] - clusterDay) == 1:
                # single-day is within 1-day of candidate acitivity span
                clusters.add(candidate)

        else:
            # add candidates into username #1 cluster
            clusters.add(candidate)

    if len(clusters) == 1:
        clusters = set()
                    
    return clusters
    
    


def eliminate_subsets(this_row, all_clusters_no_dup):
    
    this_subtotal = this_row.subtotal
    
    # See if this cluster is a subset of any other. all_clusters_no_dup is already in increasing order, without duplicates.
    
    later_clusters = all_clusters_no_dup[all_clusters_no_dup.subtotal > this_subtotal].clusters
    
    if type(this_row.clusters) == str:
        # TODO
        return False
        
    
    result = later_clusters[later_clusters>this_row.clusters]

    if result.count() == 0:
        # this cluster is not a subset of any other clusters
        return True
        
    else:
        # this cluster is a subset of some other clusters
        return False



    
def form_cluster_new(inparams, user_usage_df):
    #this program takes stuff from a file that has each line as
    #user, user, distance, user, distance...
    #where the first user is the "center" of a cluster
    #and turns it into a file that has each line being a cluster
    #user, user, user, user
    #
    #it also eliminates all subsets of other clusters so that you have
    #fewer clusters than in the input file.
    
    user_usage_indexed_df = user_usage_df.set_index('user')
    user_usage_indexed_df['userDaySpans'] = user_usage_indexed_df.apply(lambda x: (min(x.ToolUsagePattern.usages), max(x.ToolUsagePattern.usages)), axis=1)

    #
    # Forming clusters of individual users
    #
    logging.info('Forming clusters of individual users ...')
    all_clusters = user_usage_indexed_df.apply(user_cluster_formation, user_usage_indexed_df = user_usage_indexed_df, tolerance = inparams.costTolerance, axis=1)
    
    '''
    user
    fabien                          {shigeyasu, fabien, kennyxue, gsun}
    gbu                                   {aamjad, bashir, gbu, agupta}
    manolo_sperini                                                   {}
    marchi                                                           {}
    sbahl             {fervorviolinist, boz, singhd, dlsherma, tbig,...
    '''

    #
    # Forming supersets by removing smaller subsets
    #
    logging.info('Forming super cluster sets ...') 
       
    # First: remove clusters that are smaller than minimum size
    all_clusters_no_dup = all_clusters.apply(lambda x: x if len(x) >= inparams.costSizeMin else set())
        
    # Second: remove duplicates and empty
    all_clusters_no_dup = pd.DataFrame(np.unique(all_clusters_no_dup[all_clusters_no_dup != set()]), columns=['clusters'])
    all_clusters_no_dup['subtotal'] = all_clusters_no_dup['clusters'].apply(lambda x: len(x))

    # Third: combine clusters if one is a subset of another
    all_clusters_no_dup['is_not_subset'] = dd.from_pandas(all_clusters_no_dup.sample(frac=1), npartitions=200) \
                                             .apply(eliminate_subsets, all_clusters_no_dup = all_clusters_no_dup, axis=1) \
                                             .compute(scheduler=inparams.daskScheduler)
              
    return all_clusters_no_dup[all_clusters_no_dup.is_not_subset]

