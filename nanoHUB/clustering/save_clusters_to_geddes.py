from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.application import Application
from io import StringIO
import pandas as pd
import logging
import time

# geddes functionality

def save_clusters_to_geddes(clusters_dfs: {}, flags):

        print(clusters_dfs)

        # date_range_str = flags.class_probe_range.replace(':', '_')
        date_range_str = '_'.join(flags.class_probe_range)
        past_runs_folder_path = "%s/past_runs/%s/%s/by_semester/%s" % (flags.object_path, time.strftime("%Y-%m-%d"), flags.task, date_range_str)
        latest_folder_path = "%s/latest/%s/by_semester/%s" % (flags.object_path, flags.task, date_range_str)
        s3_client = get_default_s3_client(Application.get_instance())

        logging.info("Uploading output files to Geddes: %s/%s" % (flags.bucket_name, past_runs_folder_path))
        logging.info("Also uploading output files to Geddes: %s/%s" % (flags.bucket_name, latest_folder_path))
        print(flags.object_path)
        print(flags.task)
        for key, df in clusters_dfs.items():
            save_to_geddes(
                s3_client, flags.bucket_name, df, past_runs_folder_path, key
            )
            save_to_geddes(
                s3_client, flags.bucket_name, df, latest_folder_path, key
            )
            if key == 'intra_tool_cluster_df':
                intra_tool_cluster_df = pd.DataFrame(df['user_set'].values.tolist()) \
                    .rename(columns = lambda x: '{}'.format(x+1))
                save_to_geddes(
                    s3_client, flags.bucket_name, intra_tool_cluster_df, past_runs_folder_path, 'clustering_result', False
                )
                save_to_geddes(
                    s3_client, flags.bucket_name, intra_tool_cluster_df, latest_folder_path, 'clustering_result', False
                )


        # save_to_geddes(
        #     s3_client, flags.bucket_name, clusters_df, folder_path, name
        # )


        #
        #
        # df = pd.DataFrame(intra_tool_cluster_df['user_set'].values.tolist()) \
        #     .rename(columns = lambda x: '{}'.format(x+1))
        #
        # save_to_geddes(
        #     s3_client, bucket_name, df, inparams.object_path, date_range_str, False
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, students_info_df, folder_path, 'students_info_df'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, class_info_df, folder_path, 'class_info_df'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, classtool_info_df, folder_path, 'classtool_info_df'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, cluster_post_sychrony, folder_path, 'cluster_post_sychrony'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, cluster_output_candidate, folder_path, 'cluster_output_candidate'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, toolrun_df, folder_path, 'toolrun_df'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, jos_users, folder_path, 'jos_users'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, detected_clusters_df, folder_path, 'detected_clusters_df'
        # )
        # save_to_geddes(
        #     s3_client, bucket_name, user_activity_blocks_df, folder_path, 'user_activity_blocks_df'
        # )


def save_to_geddes(s3_client, bucket_name:str, df: pd.DataFrame, folder_path:str, name: str, headers:bool = True):
    _buf = StringIO()
    full_path = "%s/%s.csv" % (folder_path, name)
    df.to_csv(_buf, index=False, header=headers)
    _buf.seek(0)
    s3_client.put_object(Bucket=bucket_name, Body=_buf.getvalue(), Key=full_path)

    # logging.info("Uploaded output file to Geddes: %s/%s" % (bucket_name, full_path))
