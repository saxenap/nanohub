class Configuration:
    bucket_name_raw = 'nanohub.raw'
    bucket_name_processed = 'nanohub.processed'


class ClusteringConfiguration(Configuration):
    bucket_name_raw = 'nanohub.raw'
    bucket_name_processed = 'nanohub.processed'

    derived_data_path = 'derived_data_for_users.csv'
    nh_user_breakdown_path = 'nh_user_breakdown.csv'


class DataLakeConfiguration(Configuration):
    bucket_name_raw = 'nanohub.raw'
    bucket_name_processed = 'nanohub.processed'

    derived_data_path = 'derived_data_for_users.csv'
    nh_user_breakdown_path = 'nh_user_breakdown.csv'
    
    toolstart_path = 'nanohub_metrics/toolstart/by_semester'


class SalesforceBackupConfiguration(Configuration):
    geddes_folder_path: str = 'salesforce_backups'
    full_backups_geddes_file_path: str = 'salesforce_backups/full_backups.csv'
