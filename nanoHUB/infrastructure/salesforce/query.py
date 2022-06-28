# Created by saxenap at 6/24/22
from simple_salesforce import Salesforce
import pandas as pd
from typing import Iterator


class SalesforceObject:
    def __init__(self, name: str, client: Salesforce):
        self.name = name
        self.client = client

    def get_records(self) -> pd.DataFrame:
        sf_object = self.client.__getattr__(self.name)
        field_names = [field['name'] for field in sf_object.describe()['fields']]
        results = self.client.query_all( "SELECT " + ", ".join(field_names) + " FROM " + self.name )
        df = pd.DataFrame(results['records'])
        df.drop(columns=['attributes'], inplace=True, errors='ignore')
        return df


class SalesforceObjects:
    def __init__(self, client: Salesforce):
        self.client = client

    def get_all(self) -> Iterator[SalesforceObject]:
        description = self.client.describe()
        names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]
        for name in names:
            yield SalesforceObject(name, self.client)