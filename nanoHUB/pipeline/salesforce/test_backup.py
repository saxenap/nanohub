# Created by saxenap at 6/23/22

from simple_salesforce import Salesforce, SalesforceMalformedRequest
from argparse import ArgumentParser
from csv import DictWriter
from datetime import date
import time
from pathlib import Path
from nanoHUB.infrastructure.salesforce.contact import SalesforceFromEnvironment
from dotenv import load_dotenv
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from nanoHUB.pipeline.geddes.data import get_default_s3_client
from nanoHUB.dataaccess.lake import S3FileMapper
import os
import pandas as pd
from pprint import pprint
from requests.exceptions import ConnectionError

cwd = os.getcwd()
load_dotenv()

now = time.strftime("%Y%m%d-%H%M%S")
backup_folder = 'salesforce_backups' + '/' + now
print("Commencing backup.")
print("Time is %s", now)

datadir = os.environ['APP_DIR'] + '/' + backup_folder
print('Saving Results -> Local dir: ' + datadir)

datapath = Path(datadir)
try:
    datapath.mkdir(parents=True) #in python 3.5 we can switch to using  exist_ok=True
except FileExistsError:
    pass

application = Application.get_instance()

s3_client = get_default_s3_client(application)
raw_mapper = S3FileMapper(s3_client, ClusteringConfiguration().bucket_name_raw)

sf = SalesforceFromEnvironment('dev').create_new()

class SFQuery:
    def __init__(self, client):
        self.sf = client

    def execute(self, name: str) -> pd.DataFrame:
        sf_object = self.sf.__getattr__(name)
        field_names = [field['name'] for field in sf_object.describe()['fields']]
        results = self.sf.query_all( "SELECT " + ", ".join(field_names) + " FROM " + name )
        df = pd.DataFrame(results['records'])
        pprint(df)
        df.drop(columns=['attributes'], inplace=True, errors='ignore')
        return df

def run(sf_query, raw_mapper, name, backup_folder):
    print("Dataframe for %s" % name)
    df = sf_query.execute(name)
    outputfile = datapath / (name+".csv")
    raw_mapper.save_as_csv(df, backup_folder + '/' + name + '.csv', index=None)
    # df.to_csv(datadir + '/' + name + '.csv', index=None')

sf_query = SFQuery(sf)

description = sf.describe()
names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]

for name in names:
    while True:
        count = 0
        try:
            sf_query = SFQuery(SalesforceFromEnvironment('dev').create_new())
            run(sf_query, raw_mapper, name, backup_folder)
            break
        except SalesforceMalformedRequest as e:
            print("Malformed Request: Continuing.")
            continue
        except ConnectionError as ce:
            count = count + 1
            if count > 5:
                break
            print("Connection Error: Retrying.")
            sf_query = SFQuery(SalesforceFromEnvironment('dev').create_new())
            run(sf_query, raw_mapper, name, backup_folder)
            continue




print('Backup completed!')
print('Path %s' % backup_folder)