class Configuration:
    bucket_name_raw = 'nanohub.raw'
    bucket_name_processed = 'nanohub.processed'


class ClusteringConfiguration(Configuration):
    bucket_name_raw = 'nanohub.raw'
    bucket_name_processed = 'nanohub.processed'

    derived_data_path = 'derived_data_for_users.csv'
    nh_user_breakdown_path = 'nh_user_breakdown.csv'