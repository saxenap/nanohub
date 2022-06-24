# Created by saxenap at 6/24/22
from simple_salesforce import Salesforce
import pandas as pd


class SalesforceObject:
    def __init__(self, client: Salesforce):
        self.client = client

    def get_records_for(self, name: str) -> pd.DataFrame:
        sf_object = self.client.__getattr__(name)
        field_names = [field['name'] for field in sf_object.describe()['fields']]
        print("Querying for %s now." % name)
        results = self.client.query_all( "SELECT " + ", ".join(field_names) + " FROM " + name )
        df = pd.DataFrame(results['records'])
        df.drop(columns=['attributes'], inplace=True, errors='ignore')
        return df
