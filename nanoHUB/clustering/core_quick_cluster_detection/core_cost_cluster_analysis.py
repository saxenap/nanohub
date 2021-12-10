from pprint import pprint
import logging
import pandas as pd
import os
from io import StringIO
from .class_CommonToolUsagePair import ToolUsagePattern, CommonToolUsagePair
from .form_cluster import form_cluster_new
from .merge_clusters import merge_clusters

from dask import dataframe as dd
from dask.multiprocessing import get
from dask.diagnostics import ProgressBar

pbar = ProgressBar()
pbar.register()

import numpy as np
import datetime

import shelve
import pickle

import code
import time
from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.application import Application


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

    # Translate toolname+toolversion (pntoy_r123) into just toolname (pntoy).
    # In addition, for any toolname+toolversion not found in jos_tool_version table, treat it as toolname.
    toolrun_df = toolstart_df.join(jos_tool_version[['instance', 'toolname']].set_index('instance'), on='tool')

    # for toolnames that cannot be found in table "jos_tool_version", use tool instead
    toolrun_df['toolname'] = toolrun_df['toolname'].fillna(toolrun_df['tool'])

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

    return (toolrun_df, toolstart_df, jos_users, jos_tool_version)


def form_tool_usage_pattern(toolrun_user_df, first_day, days_span):
    tool_use = ToolUsagePattern(toolrun_user_df.name, days_span)
    toolrun_user_df.apply(lambda x: tool_use.addUsage(x.toolname, int((x.date - first_day).days)), axis=1)

    return tool_use


def cross_compare_two_users(this_user_row, user_activity_df, forceAllDifferencesLevel):
    start_time = time.time()

    # this user's row ID
    this_user_id = int(this_user_row.name)
    this_user_TUP = user_activity_df.loc[this_user_id].ToolUsagePattern

    # only compare with users whose ID is higher than this user's ID
    differences_list = list()
    for this_other_id in user_activity_df.index:
        # for each other user's ID
        if this_other_id <= this_user_id:
            continue

        other_user_TUP = user_activity_df.loc[this_other_id].ToolUsagePattern

        if not this_user_TUP.allTools.intersection(other_user_TUP.allTools):
            # the two user has no tool in common. Skip
            continue

        this_diff = CommonToolUsagePair(this_user_TUP, \
                                        other_user_TUP) \
            .getDifference(False, forceAllDifferencesLevel)
        # (tup1.user, tup2.user, diff)
        differences_list.append( \
            (user_activity_df.loc[this_other_id].user, this_diff) \
            )

    return differences_list


def core_cost_cluster_analysis(inparams):
    logging.info('Conducting Cost Cluster Analysis ...')

    #
    # Load dataframes in feathers
    #

    (toolrun_df, toolstart_df, jos_users, jos_tool_version) = prepare_data(inparams)

    # Limit analysis range to within limits

    if inparams.cost_probe_range == 'all':
        # probes only the latest (today - 3 STD of Gaussian attention window function)
        data_probe_range = [toolrun_df.date.min(), toolrun_df.date.max()]

    else:
        # probes given time range
        # expects inparams.class_probe_range in form of, for example, '2018-1-1:2018-5-1'
        datetime_range_list = inparams.cost_probe_range.split(':')
        data_probe_range = [datetime.datetime.strptime(x, '%Y-%m-%d') for x in datetime_range_list]
        logging.info(data_probe_range)

    #
    # Form user tool activity blocks
    #

    toolrun_df_within_range = toolrun_df[
        (toolrun_df.date >= data_probe_range[0]) & (toolrun_df.date <= data_probe_range[1])]

    if toolrun_df_within_range.shape[0] == 0:
        # no entry fall within the time range
        logging.info('No user activity falls within the specific time range.')
        return

    ddata = dd.from_pandas(toolrun_df_within_range, npartitions=200) \
        .groupby('user').apply(form_tool_usage_pattern, first_day=data_probe_range[0],
                               days_span=int((data_probe_range[1] - data_probe_range[0]).days)) \
        .compute(scheduler=inparams.dask_scheduler)

    user_activity_df = ddata.reset_index(
        name='ToolUsagePattern')  # reset index and form DF

    # cross-compare two users

    ddata = dd.from_pandas(user_activity_df.sample(frac=1), npartitions=200) \
        .apply(cross_compare_two_users, user_activity_df=user_activity_df,
               forceAllDifferencesLevel=inparams.cost_force_all_diff_lvl, axis=1) \
        .compute(scheduler=inparams.dask_scheduler)

    #
    # Form clusters based on costs
    #

    usages_dict = dict(
        [(user_name, obj) for user_name, obj in zip(user_activity_df.user, user_activity_df.ToolUsagePattern)])
    user_usage_df = pd.merge(ddata.rename('usages'), user_activity_df, left_index=True, right_index=True)

    clusters = form_cluster_new(inparams, user_usage_df)

    #
    # Merge similar clusters
    #

    final_clusters = merge_clusters(inparams, clusters.clusters.to_list())

    #
    # Save the final super clusters
    #
    final_clusters_df = pd.DataFrame(final_clusters)

    if inparams.display_output:
        print(final_clusters_df)

    if inparams.no_save_output == False:

        # create output directory if it does not exist
        if not os.path.exists(inparams.output_dir):
            logging.info('Creating new output directory: ' + inparams.output_dir)
            os.mkdir(inparams.output_dir)

        outfile_name = inparams.name_prefix + '_' + data_probe_range[0].strftime("%Y_%m_%d") + '-' + data_probe_range[
            1].strftime("%Y_%m_%d") + '.csv'
        outfile_filepath = os.path.join(inparams.output_dir, outfile_name)
        logging.info('Saving output files to ' + outfile_filepath)

        with open(outfile_filepath, 'w') as f:
            for this_row in final_clusters:
                f.write(','.join([str(x) for x in this_row]) + '\n')

    if inparams.save_to_geddes == True:
        bucket_name = inparams.bucket_name

        date_range_str = inparams.cost_probe_range.replace(':', '_')
        full_path = "%s/%s.csv" % (inparams.object_path, date_range_str)
        logging.debug("Uploading output file to Geddes: %s/%s" % (bucket_name, full_path))

        s3_client = get_default_s3_client(Application.get_instance())

        _buf = StringIO()
        final_clusters_df.to_csv(_buf, index=False)
        _buf.seek(0)
        s3_client.put_object(Bucket=bucket_name, Body=_buf.getvalue(), Key=full_path)

        logging.info("Uploaded output file to Geddes: %s/%s" % (bucket_name, full_path))

    logging.info("Finished cluster analysis for %s" % (inparams.cost_probe_range))