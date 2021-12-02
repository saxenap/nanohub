from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import pandas 
import os
import time
import sys
from nanoHUB.logger import logger as log
from pathlib import Path
import boto3


######################################################################################################

class Repository:
    def get_all(self) -> pandas.DataFrame:
        raise NotImplemented
        
    def get_name(self) -> str:
        raise NotImplemented


######################################################################################################

class Storage:
    def save(self, df: pandas.DataFrame):
        raise NotImplemented

    def get_name(self) -> str:
        raise NotImplemented


######################################################################################################

class ClientFactory:

    def get_client(
            endpoint_url: str, access_key: str, secret: str, service_name: str = 's3'
    ) -> boto3.session.Session.client:

        boto_session = boto3.session.Session(
            aws_access_key_id = access_key,
            aws_secret_access_key = secret
        )

        return boto_session.client(
            service_name=service_name,
            endpoint_url = endpoint_url
        )

    def init_from_config(self, application):
        return self.get_client(
            'https://' + application.get_config_value('geddesapi.endpoint') + ':443',
            application.get_config_value('geddesapi.access_key'),
            application.get_config_value('geddesapi.secret_key')
        )


class GeddesConnection:

    def __init__(self, client: boto3.session.Session.client):
        self.client = client

    def save(self, bucket_name: str, file_path: str, body: str):
        self.client.put_object(Bucket=bucket_name, Key=file_path, Body=body)

    def read(self, bucket_name: str, file_path: str):
        return self.client.get_object(Bucket=bucket_name, Key=file_path)


# class GeddesRepository(Repository):



# class Geddes(Repository, Storage):
#
#     def __init__(self, client: GeddesClient, file_path: str, format: str = 'parquet'):
#         self.client = client
#         self.file_path = file_path
#         self.format = format
#
#     def get_all(self) -> pandas.DataFrame:
#         return super().get_all()
#
#     def get_name(self) -> str:
#         return super().get_name()
#
#     def save(self, df: pandas.DataFrame):
#         return super().save(df)


######################################################################################################

class SalesforceRepository(Repository):
    def __init__(self, engine: DB2SalesforceAPI):
        self.engine = engine
        
        
class ContactsRepository(SalesforceRepository):
    def get_all(self) -> pandas.DataFrame:
        sf_user_ID_df = self.engine.query_data(
            "SELECT Id, nanoHUB_user_ID__c FROM Contact where nanoHUB_user_ID__c != NULL"
        )
        sf_user_ID_df['nanoHUB_user_ID__c'] = sf_user_ID_df['nanoHUB_user_ID__c'].astype('int')
        return sf_user_ID_df
    
    def get_name(self) -> str:
        return 'Contacts_From_Salesforce'
    

class ToolsRepository(SalesforceRepository):
    def get_all(self) -> pandas.DataFrame:
        return self.engine.query_data('SELECT Id, Tool_name__c FROM nanoHUB_tools__c')
    
    def get_name(self) -> str:
        return 'Tools_From_Salesforce'


class UnclassifiedUsers(SalesforceRepository):
    def get_all(self) -> pandas.DataFrame:
        query = '''
        SELECT Id, nanoHUB_user_ID__c
        FROM Contact
        WHERE Id NOT IN (Select Contact__c from ContactToolClusterAssociation__c)
        '''
        return self.engine.query_data(query)

    def get_name(self) -> str:
        return 'Unclassified_Users_From_Salesforce'


class ClassroomUsers(SalesforceRepository):
    def get_all(self) -> pandas.DataFrame:
        query = '''
        SELECT Id, nanoHUB_user_ID__c
        FROM Contact
        WHERE Id IN (Select Contact__c from ContactToolClusterAssociation__c)
        '''
        return self.engine.query_data(query)

    def get_name(self) -> str:
        return 'Classroom_Users_From_Salesforce'
        
######################################################################################################
    
    
class PandasRepository(Repository):
    def __init__(self, sql_string: str, engine, name: str):
        self.engine = engine
        self.sql_string = sql_string
        self.name = name
        
    def get_all(self) -> pandas.DataFrame:
        return pandas.read_sql_query(self.sql_string, self.engine)
    
    def get_name(self) -> str:
        return self.name
    
    
class CachedRepository(Repository):
    def __init__(
        self, inner: Repository, cache_folder: str, seconds_to_cache: int = 3600
    ):
        self.inner = inner
        self.cache_folder = cache_folder
        self.seconds_to_cache = seconds_to_cache
        
    def get_all(self) -> pandas.DataFrame:
        file_name = self.inner.get_name()
        suffix = '.parquet.gzip'
        
        Path(self.cache_folder).mkdir(parents=True, exist_ok=True)
        
        file_path = Path(self.cache_folder, file_name).with_suffix(suffix) 
        
        if file_path.is_file():
            ctime = os.stat(file_path).st_ctime
            seconds = time.time() - self.seconds_to_cache
            if seconds > ctime:
                os.remove(file_path)
            else:
                return pandas.read_parquet(file_path)
        
        df = self.inner.get_all()
        df.to_parquet(file_path, compression='gzip')
        
        return df

            
######################################################################################################


class RegisteredUsers(PandasRepository):
    def __init__(self, engine, name: str = 'registered_users'):
        self.engine = engine
        self.sql_string = '''
          SELECT 
      user_info.name
    , user_info.id 
    , user_info.email      
    , orcid.profile_value AS orcid
    , organization.profile_value AS organization
    , orgtype.profile_value AS orgtype
  FROM nanohub.jos_users user_info
LEFT JOIN nanohub.jos_user_profiles orgtype
  ON orgtype.user_id = user_info.id AND orgtype.profile_key = 'orgtype'
LEFT JOIN nanohub.jos_user_profiles organization
  ON organization.user_id = user_info.id AND organization.profile_key = 'organization'
LEFT JOIN nanohub.jos_user_profiles orcid
  ON orcid.user_id = user_info.id AND orcid.profile_key = 'orcid'
;
        '''
        self.name = name
        
    def get_all(self) -> pandas.DataFrame:
        return pandas.read_sql_query(self.sql_string, self.engine)  