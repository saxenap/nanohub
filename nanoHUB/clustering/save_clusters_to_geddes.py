from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.application import Application
from io import StringIO
import pandas as pd

# geddes functionality

def save_clusters_to_geddes(clusters_df, bucket_name, class_probe_range, object_path):

        date_range_str = class_probe_range.replace(':', '_')
        folder_path = "%s/%s" % (object_path, date_range_str)

        # logging.debug("Uploading output files to Geddes: %s/%s" % (bucket_name, folder_path))

        s3_client = get_default_s3_client(Application.get_instance())

        save_to_geddes(
            s3_client, bucket_name, clusters_df, folder_path, 'intra_tool_cluster_df'
        ) #intra_tool_cluster_df

        # save_to_geddes(
        #     s3_client, bucket_name, intra_tool_cluster_df['user_set'], folder_path, 'cluster_user_set', False
        # )
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

        # logging.info("Uploaded output files to Geddes: %s/%s" % (bucket_name, folder_path))

def save_to_geddes(s3_client, bucket_name:str, df: pd.DataFrame, folder_path:str, name: str, headers:bool = True):
    _buf = StringIO()
    full_path = "%s/%s.csv" % (folder_path, name)
    df.to_csv(_buf, index=False, header=headers)
    _buf.seek(0)
    s3_client.put_object(Bucket=bucket_name, Body=_buf.getvalue(), Key=full_path)

    # logging.info("Uploaded output file to Geddes: %s/%s" % (bucket_name, full_path))