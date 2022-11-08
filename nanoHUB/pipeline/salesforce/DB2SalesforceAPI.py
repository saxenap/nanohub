import pandas as pd
import requests
from io import StringIO
import time
import logging


class SalesforceFailure(RuntimeError):
    pass


class AuthenticationFailure(SalesforceFailure):
    pass


class BulkJobCreationError(SalesforceFailure):
    pass


class BulkJobFailedError(SalesforceFailure):
    pass


class ClosingJobFailedError(SalesforceFailure):
    pass


class CsvUploadFailedError(SalesforceFailure):
    pass


class DB2SalesforceAPI:
    def __init__(self, sf_login_params, endpoint: str, logger: logging.Logger):
        # Parameters
        self.endpoint = endpoint
        self.sf_login_params = sf_login_params
        self.logger = logger

        # Obtain access token
        self.obtain_token()

    def get_access_token(self):
        return self.access_token

    def get_instance_url(self) -> str:
        return self.instance_url

    def obtain_token(self):
        response = requests.post(self.endpoint, params=self.sf_login_params)

        if response.ok:
            self.access_token = response.json()['access_token']
            self.instance_url = response.json()['instance_url']
            self.logger.info('Obtained Salesforce access token ...... %s'%response.ok)

        else:
            self.logger.info('[Error] %s', response.text)
            raise AuthenticationFailure((response.json()))

    def query_data(self, query):

        # bulk get
        # Issuing a job request
        response = requests.post('https://na172.salesforce.com/services/data/v47.0/jobs/query', 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "query" : query,
                                    "operation" : "query"
                            })    

        if not response.ok:
            # job request not successful
            self.logger.info('[FAIL] Bulk job creation failed ...')
            self.logger.info(response.text)
            raise BulkJobCreationError(response.json())
        else:
            # job request successful
            self.logger.info('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']

        # wait until job is complete
        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/query/%s'%job_id, 
                                headers={"Authorization": "Bearer %s" %self.access_token}
                                )

        while response.ok:
            self.logger.info(response.text)

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
            self.logger.info('[FAIL] Bulk job failed ...')
            self.logger.info(response.text)
            raise BulkJobFailedError(response.json())
        else:
            # job request successful
            self.logger.info('[Success] Bulk job completed successfully.')

        # get result
        # Issuing a job request
        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/query/%s/results' %job_id, 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'}
                           )    

        # return dataframe
        return pd.read_csv(StringIO(response.text))





    def send_data(self, df_sf):
        # send data to Salesforce
        self.send_via_bulk(df_sf)


    def send_via_bulk(self, df_sf):
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
                                    "operation" : "upsert",
                            })    
        
        if not response.ok:
            # job request not successful
            self.logger.info('[FAIL] Bulk job creation failed ...')
            raise BulkJobCreationError(response.json())
        else:
            # job request successful
            self.logger.info('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']
        # self.logger.debug('hello')
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
            self.logger.info('[FAIL] CSV upload failed ...')
            raise CsvUploadFailedError(response.json())
        else:
            # CSV upload successful
            self.logger.info('[Success] CSV upload successful. Job ID = %s'%job_id)
        
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
            self.logger.info('[FAIL] Closing job failed ...')
            raise
        else:
            # job close successful
            self.logger.info('[Success] Closing job successful. Job ID = %s'%job_id)

            # record successful bulk
            self.bulk_job_id = job_id



    def delete_data(self, df_sf):
        # Bulk API

        # Issuing a job request
        response = requests.post('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/', 
                            headers={"Authorization": "Bearer %s" %self.access_token, 
                                     'Content-Type': 'application/json; charset=UTF-8',
                                     'Accept': 'application/json'},
                            json={
                                    "object" : self.object_id,
                                    "externalIdFieldName" : self.external_id, #not needed 
                                    "contentType" : "CSV",
                                    "lineEnding" : "LF",
                                    "operation" : "delete",
                            })
        
        if not response.ok:
            # job request not successful
            self.logger.info('[FAIL] Bulk job creation failed ...')
            raise BulkJobCreationError(response.json())
        else:
            # job request successful
            self.logger.info('[Success] Bulk job creation successful. Job ID = %s'%response.json()['id'])
        

        job_id = response.json()['id']
        # print('hello')
        # Save dataframe into CSV. Using Salesforce Bulk 2.0 API, CSV file should not exceed 150 MB
        
        bulk_csv = bytes(df_sf.to_csv(index=False,line_terminator='\n',header=True), 'utf-8').decode('utf-8','ignore').encode("utf-8")
        
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
            self.logger.info('[FAIL] CSV upload failed ...')
            raise CsvUploadFailedError(response.json())
        else:
            # CSV upload successful
            self.logger.info('[Success] CSV upload successful. Job ID = %s'%job_id)
        
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
            self.logger.info('[FAIL] Closing job failed ...')
            raise ClosingJobFailedError(response.json())
        else:
            # job close successful
            self.logger.info('[Success] Closing job successful. Job ID = %s'%job_id)

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


    def delete_job(self, job_id: str):
        response = requests.delete('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/%s' % job_id,
                                 headers={"Authorization": "Bearer %s" %self.access_token,
                                          'Content-Type': 'application/json; charset=UTF-8',
                                          'Accept': 'application/json'}
                                   )

        return response.json()


    def get_all_jobs(self):
        response = requests.get('https://na172.salesforce.com/services/data/v47.0/jobs/ingest/',
                                   headers={"Authorization": "Bearer %s" %self.access_token,
                                            'Content-Type': 'application/json; charset=UTF-8',
                                            'Accept': 'application/json'}
                                   )

        return response.json()
