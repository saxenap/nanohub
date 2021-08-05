import pandas as pd
import datetime
import requests
from io import StringIO
import time

class DB2SalesforceAPI:

    def __init__(self, sf_login_params):
        # Parameters
        self.hours_range = 24 # number of days to look back

        # API settings
        self.api_url = None
        self.external_id = None
        self.object_id = None
        self.bulk_job_id = None

        # login details
        self.sf_login_params = sf_login_params
        self.access_token = None

        # Obtain access token
        self.obtain_token()
        
    def obtain_token(self):

        # obtain access token
        response = requests.post("https://login.salesforce.com/services/oauth2/token", params=self.sf_login_params)

        if response.ok:
            self.access_token = response.json()['access_token']

            print('Obtained Salesforce access token ...... %s'%response.ok)

        else:
            print('[Error] %s', response.text)
            raise

    def query_data(self, query,sys_name = None):
        
        # platform check
        if sys_name == 'Windows':
            head_dict = {"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=cp1252',
                                     'Accept': 'application/json'}
        elif sys_name == 'Darwin' or sys_name == 'Linux':
            head_dict = {"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=ISO-8859-15',
                                     'Accept': 'application/json'}
        else:
            head_dict = {"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'}
        
        # bulk get
        # Issuing a job request
        response = requests.post('https://na172.salesforce.com/services/data/v47.0/jobs/query', 
                            headers=head_dict,
                            json={
                                    "query" : query,
                                    "operation" : "query"
                            })

        if not response.ok:
            # job request not successful
            print('[FAIL] Bulk job creation failed ...')
            print(response.text)
            raise
        else:
            # job request successful
            print('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']

        # wait until job is complete
        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/query/%s'%job_id, 
                                headers={"Authorization": "Bearer %s" %self.access_token}
                                )

        while response.ok:
            print(response.text)

            if response.json()['state'] == 'JobComplete':
                # Job has completed
                break
                
            else:
                # check job status every 10 seconds
                time.sleep(10)

            response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/query/%s'%job_id, 
                                    headers={"Authorization": "Bearer %s" %self.access_token}
                                    )

        if not response.ok:
            # job request not successful
            print('[FAIL] Bulk job failed ...')
            print(response.text)
            raise
        else:
            # job request successful
            print('[Success] Bulk job completed successfully.')

        # get result
        # Issuing a job request
        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/query/%s/results' %job_id, 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'}
                           )    

        # return dataframe
        return pd.read_csv(StringIO(response.text))





    def send_data(self, df_sf,print_flag=True):
        # send data to Salesforce
        self.send_via_bulk(df_sf,print_flag)


    def send_via_bulk(self, df_sf,print_flag):
        # Bulk API

        # Issuing a job request
        response = requests.post('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/', 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "object" : self.object_id,
                                    "externalIdFieldName" : self.external_id,
                                    "contentType" : "CSV",
                                    "operation" : "upsert"
                                    #"lineEnding" : "LF",
                                    #"columnDelimiter" : "COMMA"
                            })
        
        if print_flag == True:
            if not response.ok:
                # job request not successful
                print('[FAIL] Bulk job creation failed ...')
                raise
            else:
                # job request successful
                print('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']
        # Save dataframe into CSV. Using Salesforce Bulk 2.0 API, CSV file should not exceed 150 MB
        bulk_csv = bytes(df_sf.to_csv(index=False,line_terminator='\n'), 'utf-8').decode('utf-8','ignore').encode("utf-8")
        #bulk_csv = bytes(df_sf.to_csv(index=False), 'utf-8').decode('utf-8','ignore').encode("utf-8")
        
        
        # Put CSV content to bulk job
        # json={"body" : './temp_bulk.csv'}
        response = requests.put('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s/batches/'%job_id, 
                                headers={"Authorization": "Bearer %s" %self.access_token, 
                                         'Content-Type': 'text/csv',
                                         'Accept': 'application/json'},
                                data = bulk_csv
                                )
        if print_flag == True:
            if not response.ok:
                # CSV upload not successful
                print('[FAIL] CSV upload failed ...')
                raise
            else:
                # CSV upload successful
                print('[Success] CSV upload successful. Job ID = %s'%job_id)
        
        # Close the job, so Salesforce can start processing data
        response = requests.patch('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s'%job_id,
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "state" : "UploadComplete"
                            })  
        if print_flag == True:
            if not response.ok:
                # job close not successful
                print('[FAIL] Closing job failed ...')
                raise
            else:
                # job close successful
                print('[Success] Closing job successful. Job ID = %s'%job_id)

                # record successful bulk
                self.bulk_job_id = job_id



    def delete_data(self, df_sf):
        # delete data on Salesforce
        # Bulk API

        # Issuing a job request
        response = requests.post('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/', 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "object" : self.object_id,
                                    "contentType" : "CSV",
                                    "operation" : "delete",
                                    "lineending" : "LF",
                                    "columnDelimiter" : "COMMA"
                            })    
        
        if not response.ok:
            # job request not successful
            print('[FAIL] Bulk job creation failed ...')
            raise
        else:
            # job request successful
            print('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']
        
        # Save dataframe into CSV. Using Salesforce Bulk 2.0 API, CSV file should not exceed 150 MB
        bulk_csv = bytes(df_sf.to_csv(index=False,line_terminator='\n'), 'utf-8').decode('utf-8','ignore').encode("utf-8")
        
        # Put CSV content to bulk job
        # json={"body" : './temp_bulk.csv'}
        response = requests.put('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s/batches/'%job_id, 
                                headers={"Authorization": "Bearer %s" %self.access_token, 
                                         'Content-Type': 'text/csv',
                                         'Accept': 'application/json'},
                                data = bulk_csv
                                )
        
        if not response.ok:
            # CSV upload not successful
            print('[FAIL] CSV upload failed ...')
            raise
        else:
            # CSV upload successful
            print('[Success] CSV upload successful. Job ID = %s'%job_id)
        
        # Close the job, so Salesforce can start processing data
        response = requests.patch('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s'%job_id,
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "state" : "UploadComplete"
                            })  
        
        if not response.ok:
            # job close not successful
            print('[FAIL] Closing job failed ...')
            raise
        else:
            # job close successful
            print('[Success] Closing job successful. Job ID = %s'%job_id)

            # record successful bulk
            self.bulk_job_id = job_id



    def check_bulk_status(self):
        # check bulk upload status

        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s'%self.bulk_job_id, 
                            headers={"Authorization": "Bearer %s" %self.access_token}
                            )

        return response.json()


    def check_bulk_failed_results(self):
        # check bulk upload status

        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s/failedResults/'%self.bulk_job_id, 
                            headers={"Authorization": "Bearer %s" %self.access_token}
                            )

        return response.text


    def get_obj_metadata(self, object_name):
        # utility function. Obtain object's metadata

        response = requests.get('https://na172.salesforce.com/services/data/v47.0/sobjects/%s/describe/'%object_name, 
                            headers={"Authorization": "Bearer %s" %self.access_token}
                            )

        return response.text
