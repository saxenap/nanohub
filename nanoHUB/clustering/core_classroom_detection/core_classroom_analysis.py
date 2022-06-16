import multiprocessing
from pprint import pprint
import logging
import pandas as pd
from dask.dataframe import from_pandas
import os

from .combine_clusters import combine_clusters, haversine_metric, haversine_affinity

import geoip2.database

# from dask import dataframe as dd
# from dask.multiprocessing import get
# from dask.diagnostics import ProgressBar

import numpy as np
import datetime

from sklearn.cluster import AgglomerativeClustering, DBSCAN

import shelve
import pickle

import code

from functools import partial
from io import StringIO
from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.application import Application
#
# Load geospatial data
#

def get_geo_data(inparams, ip):
    try:
        reader = geoip2.database.Reader(inparams.geoip2_mmdb_filepath)
        response = reader.city(ip)
        return [response.location.longitude, response.location.latitude]

    except:
        return [None, None]


def get_scratch_dir(inparams):
    return os.path.join(inparams.scratch_dir, inparams.class_probe_range[0] + '_' + inparams.class_probe_range[1])


def prepare_data(inparams):
    #
    # Load dataframes in feathers
    #

    logging.info('Loading relevent data ...')

    toolstart_df = pd.read_feather(
        get_scratch_dir(inparams) + '/toolstart.feather'
    )
    toolstart_df['tool'] = toolstart_df['tool'].apply(lambda x: x.lower())


    jos_tool_version = pd.read_feather(
        get_scratch_dir(inparams) + '/jos_tool_version.feather'
    )

    jos_users = pd.read_feather(
        get_scratch_dir(inparams) + '/jos_users.feather'
    )

    # for toolnames that cannot be found in table "jos_tool_version", use tool instead
    toolrun_df = toolstart_df.join(jos_tool_version[['instance', 'toolname']].set_index('instance'), on='tool')

    # remove all rows with protocol != 5,6,7
    toolrun_df = toolrun_df[toolrun_df['protocol'].isin([5, 6, 7])]

    # remove several user that are not actual person
    toolrun_df = toolrun_df[toolrun_df.user != 'instanton']

    # convert datetime to date only
    toolrun_df['date'] = toolrun_df['datetime'].dt.floor('D')

    # remove column 'tool', 'datetime', and 'protocol'. They are not used anymore
    toolrun_df = toolrun_df.drop(columns=['tool', 'protocol', 'datetime'])

    # drop duplicate rows
    toolrun_df.drop_duplicates(inplace=True)

    # pbar = ProgressBar() # this is a feature from Dask (removed)
    # pbar.register()

    # partial(): gives the function get_geo_data its first parameter,
    # it allows us to fix a certain number of arguments of a function
    # and generate a new function，get_geo_data_partial.
    get_geo_data_partial = partial(get_geo_data, inparams)

    # made a pool and use map() to give a list of single parameters
    # pool.map() accepts only a list of single parameters as input.
    # Multiple parameters can be passed to pool by a list of parameter-lists,
    # or by setting some parameters constant using partial.
    # A prime example of this is the Pool object which offers a convenient means of parallelizing the execution
    # of a function across multiple input values, distributing the input data across processes (data parallelism).
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        geo_data = pool.map(get_geo_data_partial, toolrun_df['ip'])

    geo_data = np.array(geo_data, dtype=np.float32)

    lon_lat = np.stack(geo_data)
    toolrun_df['lon'] = lon_lat[:, 0].astype(np.float)
    toolrun_df['lat'] = lon_lat[:, 1].astype(np.float)

    logging.info('Longitude and Latitude assigned user tool run activities')
    logging.info('(toolrun_df)')
    # logging.info(toolrun_df)

    return (toolrun_df, toolstart_df, jos_users, jos_tool_version)


def form_activity_blocks(activity_tol, user_df):
    # given a user's DF, form activity blocks for each of the tool
    user_tools = user_df[1]['toolname'].unique()

    activity_blocks = list()

    for this_tool in user_tools:
        # tools from each user, sort from latest to earliest
        tooluse_df = user_df[1][user_df[1].toolname == this_tool].sort_values('date', ascending=False)
        # start from latest date (present)

        try:
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
        except IndexError:
            pass

    # add username to dataframe
    # activity_blocks['user'] = user_df.user.unique()
    activity_blocks = {(user_df[0], i): activity_blocks[i] for i in range(len(activity_blocks))}
    return pd.DataFrame(activity_blocks, index=['tool', 'start', 'end', 'ip']).T


def geospatial_cluster(cluster_size_cutoff, class_distance_threshold, cluster_input):
    """
    Given individual user's activity blocks for all users, all days, use geospatial clustering
    to form clusters with certrain intra-cluster distance limit.
    """
    date_earliest = cluster_input[1].start.min()
    date_latest = cluster_input[1].end.max()
    # logging.info('Date range: '+str(date_earliest)+' - '+str(date_latest))

    cluster_output = list()
    cluster_input[1]['cluster'] = None
    cluster_input[1]['scanned_date'] = datetime.datetime(1900, 1, 1)

    cluster_output_np = np.empty((0, len(cluster_input[1].columns)))


    for this_date in [date_earliest + datetime.timedelta(days=n) for n in
                      range(0, int((date_latest - date_earliest).days + 1))]:

        # for each date spanned by cluster_input[1]

        this_date_all_blocks = cluster_input[1][
            (cluster_input[1].start <= this_date) & (cluster_input[1].end >= this_date)]

        this_date_all_tools = this_date_all_blocks.tool.unique()

        for this_tool in this_date_all_tools:
            this_date_cluster_input = this_date_all_blocks[this_date_all_blocks.tool == this_tool]

            # if sample too small, skip
            if len(this_date_cluster_input.index) < cluster_size_cutoff:
                continue

            # number of users for this tool is large enough, globally, to warrent a geospatial clustering
            this_clustering = AgglomerativeClustering(affinity=haversine_affinity, \
                                                      linkage='average', \
                                                      n_clusters=None, \
                                                      distance_threshold=class_distance_threshold \
                                                      ).fit(this_date_cluster_input[['lon', 'lat']].values)

            cluster_input[1].loc[this_date_cluster_input.index, 'cluster'] = this_clustering.labels_
            cluster_input[1].loc[this_date_cluster_input.index, 'scanned_date'] = this_date

            # add this tool run's scanned_date, tool, user into dict
            cluster_output_np = np.append(cluster_output_np,
                                          cluster_input[1].loc[this_date_cluster_input.index].to_numpy(), axis=0)

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
                    if this_candidate['last_update'] != all_scanned_dates[index - 1]:
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
                all_clusters.append({'last_update': this_date, 'users_row_id': this_cluster_df.index})
                # display('adding '+str(len(this_cluster_df.index))+' rows')

    # turn into a dataframe
    all_clusters_df = pd.DataFrame(all_clusters)
    all_clusters_df.drop('last_update', axis=1, inplace=True)

    # find the earliest start and latest end of all users within cluster
    all_clusters_df['start'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].start.min(), axis=1)
    all_clusters_df['end'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].end.max(), axis=1)

    # find number of users involved in this detected super cluster
    all_clusters_df['user_count'] = all_clusters_df.apply(
        lambda x: len(tool_clusters_df.loc[x.users_row_id].user.unique()), axis=1)

    # find the average coordinate
    try:
        # avoid a DASK bug
        all_clusters_df['mean_lat'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].lat.mean(),
                                                            axis=1)
        all_clusters_df['mean_lon'] = all_clusters_df.apply(lambda x: tool_clusters_df.loc[x.users_row_id].lon.mean(),
                                                            axis=1)
    except:
        all_clusters_df['mean_lat'] = all_clusters_df.apply(lambda x: None, axis=1)
        all_clusters_df['mean_lon'] = all_clusters_df.apply(lambda x: None, axis=1)

    all_clusters_df['lat_lon'] = all_clusters_df.apply(lambda x: list(
        zip(tool_clusters_df.loc[x.users_row_id].lat.values, tool_clusters_df.loc[x.users_row_id].lon.values)), axis=1)

    return all_clusters_df


def get_toolrun_vector(this_user_toolrun, cluster_date, sigma, all_tool_names):
    '''
    Given the user's toolrun history, cluster's datetime, and all tools used by this cluster's users,
    get the toolrun vector for this user
    '''

    # apply Guassian filter to toolrun
    normal_df = this_user_toolrun.groupby('toolname').apply(lambda x: \
                                                                np.exp(-1 * (x.date - cluster_date).astype(
                                                                    'timedelta64[D]').to_numpy() ** 2 / sigma) \
                                                            ) \
        .apply(np.sum)

    # TEST: No Guassian filter
    normal_df = this_user_toolrun.groupby('toolname').user.count()

    # form normalized vector
    normal_df = normal_df.reindex(all_tool_names, fill_value=0)
    v_length = np.linalg.norm(normal_df)
    normal_df = normal_df / v_length if v_length > 0 else None

    return normal_df


def intra_cluster_synchrony_pregroup(toolrun_df, this_cluster_group):
    '''
    Buffer function between Dask and actual synchrony computation to have flexible control of parallelism
    '''

    # get DBSCAN intra-cluster refinement
    this_result = this_cluster_group[1].groupby(['scanned_date', 'cluster']).apply(intra_cluster_synchrony,
                                                                                   toolrun_df=toolrun_df)

    # remove all -1 non-cluster members
    if not this_result.empty:
        this_result = this_result[this_result.DBSCAN > -1]

    # remove all sub-groups (cluster, DBSCAN) that are smaller than minimal size requirement

    return this_result


def intra_cluster_synchrony(this_cluster, toolrun_df):
    '''
    Reject any candidate within the cluster that is out-of-sync with others.
    '''
    # find the 2 sdev dates on left and right side tails of Gaussian
    cluster_date = this_cluster.name[0]
    # display('----- cluster_date:', cluster_date)
    # display('----- cluster_tool:', this_cluster.name[1])
    sigma = 10  # days

    start_datetime = cluster_date - datetime.timedelta(days=sigma)
    end_datetime = cluster_date + datetime.timedelta(days=sigma)

    # get each user's timeline behavior
    toolrun_within_range_df = toolrun_df[ \
        (toolrun_df.date >= start_datetime) & \
        (toolrun_df.date <= end_datetime) \
        ]

    this_user_set = this_cluster.user.unique()

    is_user_within_cluster = toolrun_within_range_df.apply(lambda x: x.user in this_user_set, axis=1)
    if not is_user_within_cluster.empty:
        this_cluster_users_toolrun = toolrun_within_range_df[is_user_within_cluster] \
            .sort_values(by=['user', 'date'])
    else:
        return

    this_cluster_all_tools = this_cluster_users_toolrun.toolname.unique()

    # for each user, calculate its sychrony
    tool_vector = this_cluster_users_toolrun.groupby('user').apply(get_toolrun_vector, \
                                                                   cluster_date=cluster_date, sigma=sigma, \
                                                                   all_tool_names=this_cluster_all_tools)

    # remove all-zero rows
    '''
    display('----- this_cluster_users_toolrun')
    display(this_cluster_users_toolrun)
    display('----- tool_vector')
    display(tool_vector)
    display('----- tool_vector_2')
    '''
    tool_vector = tool_vector[~tool_vector[tool_vector.columns[0]].isna()]

    # clustering
    cluster = DBSCAN(min_samples=2, eps=0.6)
    cluster_result = cluster.fit_predict(tool_vector.to_numpy())

    tool_vector['_group'] = cluster_result
    # display(tool_vector.sort_index(axis=1))

    this_cluster['DBSCAN'] = cluster_result

    return this_cluster


def core_classroom_analysis(inparams):
    logging.info('Conducting Classroom Analysis ...')

    #
    # Load dataframes in feathers
    #

    (toolrun_df, toolstart_df, jos_users, jos_tool_version) = prepare_data(inparams)

    # Limit analysis range to within limits

    logging.info(
        'Probing range: ' + inparams.class_probe_range[0] + ' - ' + inparams.class_probe_range[1])

    #
    # Form user tool activity blocks
    #
    activity_tol = datetime.timedelta(days=inparams.class_activity_tol)
    # ddata = dd.from_pandas(toolrun_df, npartitions=200) \
    #           .groupby('user').apply(form_activity_blocks, activity_tol = activity_tol) \
    #           .compute(scheduler=inparams.dask_scheduler)

    form_activity_blocks_partial = partial(form_activity_blocks, activity_tol)

    grouped = toolrun_df.groupby('user')

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        ddata = pool.map(form_activity_blocks_partial, [(name, group) for name, group in grouped])
    ddata = pd.concat(ddata)
    ddata.index.names = ['user', None]


    user_activity_blocks_df = ddata[
        (ddata.start >= inparams.data_probe_range[0]) & (ddata.end <= inparams.data_probe_range[1])] \
        .reset_index().drop(['level_1'], axis=1)

    #
    # Geospatial clustering
    #

    # join the IP and Lat, Lon
    user_activity_blocks_df = pd.merge(user_activity_blocks_df, toolrun_df[['ip', 'lon', 'lat']].drop_duplicates(),
                                       on='ip', how='left')

    # remove all NaN entries in Lat and Lon
    user_activity_blocks_df = user_activity_blocks_df[
        ~user_activity_blocks_df.lat.isna() & ~user_activity_blocks_df.lon.isna()]

    logging.info('Tool usage activity blocks formed for each user for all days')
    logging.info('(user_activity_blocks_df)')
    logging.info(user_activity_blocks_df)

    # Geospatial clustering for each day, each tool
    grouped = user_activity_blocks_df.groupby('tool')
    geospatial_cluster_partial = partial(geospatial_cluster, inparams.class_size_min, inparams.class_distance_threshold)
    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        ddata = pool.map(geospatial_cluster_partial, [(name, group) for name, group in grouped])

    detected_clusters_df = pd.DataFrame(np.vstack(ddata), columns=(
            user_activity_blocks_df.columns.to_list() + ['cluster', 'scanned_date']))

    # remove duplicated: same user, same tool, appearing in the same cluster more than once
    cluster_output_nodup = detected_clusters_df.drop_duplicates(subset=['scanned_date', 'cluster', 'user', 'tool'])

    passed_cutoff = cluster_output_nodup[['scanned_date', 'cluster', 'tool', 'user']]
    passed_cutoff = passed_cutoff.groupby(['scanned_date', 'cluster', 'tool']).count()['user'] > inparams.class_size_min

    cluster_output_candidate = cluster_output_nodup.join(passed_cutoff, on=['scanned_date', 'cluster', 'tool'],
                                                         rsuffix='_meet_class_size_min')
    cluster_output_candidate['user_meet_class_size_min'].fillna(False, inplace=True)
    cluster_output_candidate = cluster_output_candidate[cluster_output_candidate.user_meet_class_size_min]

    logging.info('Geospatially clustered candidates for classrooms on each day:')
    logging.info('(cluster_output_candidate)')
    logging.info(cluster_output_candidate)

    # Aggregate clusters in neighboring days into one
    '''
    code.interact(local=locals())
    ddata = dd.from_pandas(cluster_output_candidate, npartitions=60) \
              .groupby('tool').apply(form_cluster_blocks) \
              .compute(scheduler=inparams.dask_scheduler)
    #'end', 'mean_lat', 'mean_lon', 'start', 'user_count', 'users_row_id'
    class_cluster_candidate = ddata.reset_index()
    logging.info('Class candidates formed for each user for all days')
    logging.info('(class_cluster_candidate)')
    logging.info(class_cluster_candidate)
    '''

    # NOTEBOOK CHECKPOINT
    if inparams.generate_notebook_checkpoints:
        logging.info('Generating Jupyter Notebook checkpoint 1: Synchrony EDA')

        # class_cluster_candidate.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_class_cluster_candidate.pkl'))
        # user_activity_blocks_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_user_activity_blocks_df.pkl'))
        # detected_clusters_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_detected_clusters_df.pkl'))
        # jos_users.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_jos_users.pkl'))
        # toolrun_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_toolrun_df.pkl'))
        # cluster_output_candidate.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_cluster_output_candidate.pkl'))
        #
        # with open(os.path.join(inparams.scratch_dir, 'core_classroom_analysis_cp1.pkl'), 'wb') as f:
        #     pickle.dump([inparams], f)

    #
    # Sychrony check for each cluster. Remove false positives and split cluster if multiple sub-clusters detected
    #

    # add new column for DBSCAN results. Default to non-member (-1)
    cluster_output_candidate['DBSCAN'] = -1
    intra_cluster_synchrony_pregroup_partial = partial(intra_cluster_synchrony_pregroup, toolrun_df)
    grouped = cluster_output_candidate.groupby('tool')

    with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
        cluster_post_sychrony = pool.map(intra_cluster_synchrony_pregroup_partial,
                                         [(name, group) for name, group in grouped])

    cluster_post_sychrony = pd.concat(cluster_post_sychrony)

    # drop 'tool' index which is duplicate of the 'tool' column
    cluster_post_sychrony = cluster_post_sychrony.reset_index(drop=True)

    # NOTEBOOK CHECKPOINT
    if inparams.generate_notebook_checkpoints:
        logging.info('Generating Jupyter Notebook checkpoint 2: Post-Synchrony EDA')

        cluster_post_sychrony.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_cluster_post_sychrony.pkl'))

    #
    # Combine clusters into super-clusters
    #

    intra_tool_cluster_df, students_info_df, class_info_df, classtool_info_df = combine_clusters(inparams,
                                                                                                 cluster_post_sychrony)
    

    # # NOTEBOOK CHECKPOINT
    # if inparams.generate_notebook_checkpoints:
    #     logging.info('Generating Jupyter Notebook checkpoint 3: Program complete')
    #
    #     intra_tool_cluster_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_intra_tool_cluster_df.pkl'))
    #     students_info_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_students_info_df.pkl'))
    #     class_info_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_class_info_df.pkl'))
    #     classtool_info_df.to_pickle(os.path.join(inparams.scratch_dir, 'cp1_classtool_info_df.pkl'))

    logging.info("Finished cluster analysis for %s" % (inparams.cost_probe_range))

    return intra_tool_cluster_df

    #geddes functionality

    # if inparams.save_to_geddes == True:
    #     bucket_name = inparams.bucket_name
    #
    #     date_range_str = inparams.cost_probe_range.replace(':', '_')
    #     folder_path = "%s/%s" % (inparams.object_path, date_range_str)
    #
    #     logging.debug("Uploading output files to Geddes: %s/%s" % (bucket_name, folder_path))
    #
    #     s3_client = get_default_s3_client(Application.get_instance())
    #
    #     save_to_geddes(
    #         s3_client, bucket_name, intra_tool_cluster_df, folder_path, 'intra_tool_cluster_df'
    #     )
    #
    #     save_to_geddes(
    #         s3_client, bucket_name, intra_tool_cluster_df['user_set'], folder_path, 'cluster_user_set', False
    #     )
    #
    #     df = pd.DataFrame(intra_tool_cluster_df['user_set'].values.tolist()) \
    #         .rename(columns = lambda x: '{}'.format(x+1))
    #
    #     save_to_geddes(
    #         s3_client, bucket_name, df, inparams.object_path, date_range_str, False
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, students_info_df, folder_path, 'students_info_df'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, class_info_df, folder_path, 'class_info_df'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, classtool_info_df, folder_path, 'classtool_info_df'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, cluster_post_sychrony, folder_path, 'cluster_post_sychrony'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, cluster_output_candidate, folder_path, 'cluster_output_candidate'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, toolrun_df, folder_path, 'toolrun_df'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, jos_users, folder_path, 'jos_users'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, detected_clusters_df, folder_path, 'detected_clusters_df'
    #     )
    #     save_to_geddes(
    #         s3_client, bucket_name, user_activity_blocks_df, folder_path, 'user_activity_blocks_df'
    #     )
    #
    #     logging.info("Uploaded output files to Geddes: %s/%s" % (bucket_name, folder_path))

def save_to_geddes(s3_client, bucket_name:str, df: pd.DataFrame, folder_path:str, name: str, headers:bool = True):
    _buf = StringIO()
    full_path = "%s/%s.csv" % (folder_path, name)
    df.to_csv(_buf, index=False, header=headers)
    _buf.seek(0)
    s3_client.put_object(Bucket=bucket_name, Body=_buf.getvalue(), Key=full_path)

    logging.info("Uploaded output file to Geddes: %s/%s" % (bucket_name, full_path))