from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import pandas 
import os
import time
import sys
from nanoHUB.logger import logger as log
from pathlib import Path


class Repository:
    def get_all(self) -> pandas.DataFrame:
        raise NotImplemented
        
    def get_name(self) -> str:
        raise NotImplemented
        

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

    
