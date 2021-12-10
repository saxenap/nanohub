from nanoHUB.application import Application
from nanoHUB.pipeline.geddes.data import map, QueryString, get_default_s3_client
import datetime


application = Application.get_instance()
nanohub_metrics_db = application.new_db_engine('nanohub')

s3_client = get_default_s3_client(application)

query = QueryString(
    'nanohub',
    'jos_users',
    'registerDate',
    'registerDate',
    ['name', 'username', 'email', 'approved', 'registerDate', 'lastvisitDate', 'activation'],
    ['registerDate', 'lastvisitDate']
)
bucket_name = 'nanohub.raw'
from_date = datetime.date(2005,1,1)
end = datetime.date.today()

map(
    query, nanohub_metrics_db, s3_client, bucket_name, from_date
)


