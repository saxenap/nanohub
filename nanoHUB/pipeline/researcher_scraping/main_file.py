# -*- coding: utf-8 -*-
"""
Created on Fri May 4 13:37:10 2021

@author: henry
"""
# %% import packages

## Levenshtein distance handler
from Levenshtein import distance as levenshtein_distance

import sys
#sys.path.append('/home/users/wang2506/nanohub_salesforce_integ/salesforce')
import os
import pandas as pd
import time
import datetime

#from DB2SalesforceAPI import DB2SalesforceAPI

from IPython.display import display

from scholarly import scholarly, ProxyGenerator
from fp.fp import FreeProxy
import time
import numpy as np

from googlesearch import search
import re

from pprint import pprint

import logging
import os

from nanoHUB.application import Application

application = Application.get_instance()
# nanohub_db = application.new_db_engine('nanohub')
# nanohub_metrics_db = application.new_db_engine('nanohub_metrics')
# wang159_myrmekes_db = application.new_db_engine('wang159_myrmekes')

salesforce = application.new_salesforce_engine()
db_s = salesforce


cwd = os.getcwd()
APP_DIR =  os.getenv('APP_DIR')

# %% logging dir make
try:
    os.mkdir(cwd+'/logging')
except:
    print("logging dir exists, you're good")

# %% description

###
# Objective: obtain researcher ids
# Google Scholar ID_sf: scholar scrape 
# ORCID_sf: ORCID research id search
# Research ID_sf: web of science id search [ORCID can filter] - search as publons
# SCOPUS ID_sf: scopus id search [ORCID can filter]
# reseach gate: either google or own url search 
## Social media scraper
# Facebook via standard google search
# twitter ""
# linkedin ""
# personal websites/webpages: appended to Misc_URLs__c
###



# %% Pull in SF contacts and filter them

# API settings
api_url = '/services/data/v43.0/sobjects'
external_id = 'Name'
object_id = 'ContactToolAssociation__c'

# # login parameters to be handled by Papermill
# sql_login_params = {"username": "wang2506_ro", "password": "fnVnwcCS7iT45EsA"}
# sf_login_params = {
#     "grant_type": "password",
#     "client_id": "3MVG95jctIhbyCppj0SNJ75IsZ1y8UPGZtSNF4j8FNVXz.De8Lu4jHm3rjRosAtsHy6qjHx3i4S_QbQzvBePG",
#     "client_secret": "D1623C6D3607D4FC8004B92C761DFB6C1F70CCD129C5501E357028DFA00F5764",
#     "username":"wang2506@purdue.edu",
#     "password":"npass2021HDfJLhBGDx11xWCKlEbHQKhF",   
# }

# db_1 = DB2SalesforceAPI(sf_login_params)
db_1 = db_s

query = 'Select ID, firstname, lastname, Email, nanoHUB_user_ID__c, \
    Google_Scholar_ID_sf__c, ORCID_sf__c, Research_ID_sf__c, ResearchGate_ID_sf__c, \
    ResearcherPresence_sf__c, ResearchPresence_Notes_sf__c, \
    Linkedin_Bio__c, Facebook_profile__c, Twitter_profile__c, Misc_URLs__c, \
    Organization_composite__c, Active_duration__c \
    from Contact' #import everyone # limit 10'

cwd = APP_DIR + '/nanoHUB/pipeline/researcher_scraping'
c_sample_file_path = cwd + '/scrape_results/c_sample.csv'
try:
    c_sample = pd.read_csv(c_sample_file_path)
    c_sample = c_sample.drop(columns='Unnamed: 0')
except:
    # raise TypeError('temp error msg')
    c_sample = db_1.query_data(query)
    c_sample.to_csv(c_sample_file_path)

display(c_sample.head(2))
display(c_sample.tail(2))

# %% avoid re-querying
## sort/filter c_sample based on active durations

c_sample = c_sample.sort_values(by='Active_duration__c',ascending = False)

## filter the contacts st we have valid emails for possible researchers
c_sample2 = c_sample.dropna(subset=['Email','LastName','FirstName',\
        'nanoHUB_user_ID__c','Active_duration__c'])
c_sample2 = c_sample2.reset_index().drop(columns='index')
display(c_sample2.head(2))
display(c_sample2.tail(2))

## determine email domains
email_domains = c_sample2['Email'].to_list()

for i,j in enumerate(email_domains):
    j_temp = j.split('@')
    email_domains[i] = j_temp[-1]

print(email_domains[:3])


# %% Organization Pointer Fill 

##
# 1. pull SF organization codes 
# 2. replace pointers in c_sample (i.e., Organization_composite__c col) with the corresponding org name
##

orgs_query = 'Select ID, Name, Domain__c from organization__c'
try:
    orgs_all = pd.read_csv(cwd+'/scrape_results/orgs_all.csv')
except:
    orgs_all = db_1.query_data(orgs_query)
    orgs_all = orgs_all.rename(columns={'Id':'Organization_composite__c'})
    orgs_all.to_csv(cwd+'/scrape_results/orgs_all.csv')

# left inner join
c_sample2 = c_sample2.merge(orgs_all,how='left',on='Organization_composite__c',\
                suffixes=[None,'Delete'])

c_sample2 = c_sample2.rename(columns={'Name':'org_name'})

# extract org names for later comparisons
org_names = c_sample2['org_name'].to_list()

# %% master loop
batch_size = 20

def batch(iterable, n=1):
    l = len(iterable)
    temp_list = []
    for ndx in range(0, l, n):
        temp_list.append(iterable[ndx:min(ndx + n, l)])
    return temp_list

# for x in batch(range(0, 10), 3):
#     print(x)

# split indexes into batches based on bs
counter =  0

# determine the batch number
batch_no = 0
batch_e_flag = False
while batch_e_flag == False:
    try:
        tt_batch = pd.read_excel(cwd+'/scrape_results/batch_results_'\
                                 +str(batch_no)+'.xlsx')
        batch_no += 1
    except:
        batch_e_flag = True

proxy_flag = False 

start_t = time.time()
for instance in batch(range(c_sample2.shape[0]),batch_size)[batch_no:]: ## TODO : debug flag, revert to 0
    instance = list(instance)
    temp_sample = c_sample2.iloc[instance,:]

    ## %% Google_Scholar_ID_sf__c search
    
    ## details: https://scholarly.readthedocs.io/en/latest/quickstart.html
    # preamble: proxy bypass google scholar bot wall via free-proxy [if fails, link to internal tor w/in brave docs]
    # 1. extract and combine firstname and lastname in a list
    # 2. search via scholarly - store generators
    # 3. filter results for firstname/lastname + email combination
    #    - email/domain + firstname/lastname > email > firstname + lastname comb
    # 4. if exists, build google scholar url
    # 5. populate dataframe with the results
    ##
    
    while proxy_flag == False:
        time.sleep(5)
        try:
            pg = ProxyGenerator()
            pg.FreeProxies()
            scholarly.use_proxy(pg)
            proxy_flag = True
        except:
            proxy_flag = False
    
    
    def names_calc(in_df,dump_mid=False,exact=False):
        fullnames = []
        for i in range(in_df.shape[0]):
            temp_fn = ' '.join([in_df.iloc[i,3],in_df.iloc[i,6]])
            
            # dump middle name - issues with exact searches
            if dump_mid == True:
                temp_fn_list = temp_fn.split(' ') # otherwise if fn = n1 n2, then wont get list form
                if len(temp_fn_list) >= 3:
                    fullnames.append(' '.join([temp_fn_list[0],temp_fn_list[-1]]))
                else:
                    fullnames.append(' '.join(temp_fn_list))
            else:
                fullnames.append(temp_fn)
            
            # convert fullnames into exact strings
            if exact == True:
                fullnames[-1] = '"' + fullnames[-1] + '"'
            
        return fullnames
    
    # fullnames list
    fullnames = names_calc(temp_sample)
    
    gs_ids = [] #google scholar IDs
    
    # search iteratively and store
    for ind,val in enumerate(fullnames):
        # print(gs_ids)
        author_gen = scholarly.search_author(val)
        
        list_auth_gen = []
        auth_gen_count = 0
        auth_cap = 3
        for temp_auth in author_gen:
            if auth_gen_count >= auth_cap:
                break
            else:        
                list_auth_gen.append(temp_auth)
                auth_gen_count += 1
        
        # time.sleep(np.random.randint(5,15)) # rng seconds of sleep
        
        print(gs_ids)
        
        try:
            if len(list_auth_gen) != 0:
                # iteratively perform name based levenshtein capping
                counter = 0
                for test_case in list_auth_gen:
                    if levenshtein_distance(test_case['name'],val) <= 5: #less than or equal to 5 edits
                        if test_case['email_domain'] == email_domains[ind]:
                            # .edu domains
                            if email_domains[ind][-3:] == 'edu':
                                gs_url = 'https://scholar.google.com/citations?user={}&hl=en&oi=ao'.format(test_case['scholar_id'])
                                gs_ids.append(gs_url)
                                break
                            else: #hack
                                gs_url = 'https://scholar.google.com/citations?user={}&hl=en&oi=ao'.format(test_case['scholar_id'])
                                gs_ids.append(gs_url)
                                break
                        elif test_case['affiliation'] == org_names[ind]:
                            gs_url = 'https://scholar.google.com/citations?user={}&hl=en&oi=ao'.format(test_case['scholar_id'])
                            gs_ids.append(gs_url)
                            break
                    
                    counter += 1
                    if counter == len(list_auth_gen):
                        try:
                            gs_url = 'https://scholar.google.com/citations?user={}&hl=en&oi=ao'.format(list_auth_gen[0]['scholar_id'])
                            gs_ids.append(gs_url)
                        except:
                            print('move on - no google scholar result')
                        break
            else:
                gs_ids.append('')
        except:
            gs_ids.append('')
    # print(gs_ids)
    # print(len(gs_ids))
    
    # print(fullnames)
    # print(len(fullnames))
    temp_sample['Google_Scholar_ID_sf__c'] = gs_ids
    display(temp_sample.head(5))

    time.sleep(np.random.randint(2,10))

    ## %% ORCID search
    
    ## details: rely on the fullnames list created earlier
    # 1. design ORCID search URLs to find candidate ORCIDs
    # 2. iteratively search through possible ORCID urls
    # 3. levensthein distance calculation for organization [not done - adds variance to gs results]
    # 4. [far future] if need more thoroughness can use https://orcid.github.io/orcid-api-tutorial/; although this is overkill
    ##
    
    ORCID_urls = []
    
    # populate ORCID urls
    for i in fullnames:
        temp_name = i.split(' ')
        test = search('{} {} ORCID'.format(temp_name[0],temp_name[-1]),tld='com', lang='en', \
                      num=5, start=0, stop=5, pause=np.random.randint(2,5))
        list_test = [j for j in test]
        if len(list_test) == 0:
            ORCID_urls.append('')
        else:   
            for ind,j in enumerate(list_test):
                orcid_matches = re.findall(r'orcid.org/\d+-\d+-\d+-\d+',j)
                if len(orcid_matches) > 0:
                    # take the first match and move on
                    temp_url = 'https://{}'.format(orcid_matches[0])
                    ORCID_urls.append(temp_url)
                    break
    
                if ind == len(list_test)-1:
                    ORCID_urls.append('')
                    break
                
    temp_sample['ORCID_sf__c'] = ORCID_urls
    time.sleep(np.random.randint(2,10))
        
    ## %% reseach gate    
    ## Follow procedure from ORCID + publons
    research_gate_ids = [] #web of science researcherIDs
    
    # populate research gates
    for i in fullnames:
        temp_name = i.split(' ')
        test = search('{} {} research gate'.format(temp_name[0],temp_name[-1]),tld='com', lang='en', \
                      num=5, start=0, stop=5, pause=np.random.randint(2,5))
        list_test = [j for j in test]
        if len(list_test) == 0:
            research_gate_ids.append('')
        else:
            for ind,j in enumerate(list_test):
                rg_matches = re.findall(r'researchgate.net/profile/\w+-\w+',j)
                if len(rg_matches) > 0:
                    # take the first match and move on
                    temp_url = 'https://{}'.format(rg_matches[0])
                    research_gate_ids.append(temp_url)
                    break
    
                if ind == len(list_test)-1:
                    research_gate_ids.append('')
                    break
    
    temp_sample['ResearchGate_ID_sf__c'] = research_gate_ids
    time.sleep(np.random.randint(2,10))
    
    
    ## %% type adjustment for NH user ids and then upload to SF
    temp_sample['nanoHUB_user_ID__c'] = \
        temp_sample['nanoHUB_user_ID__c'].apply(lambda x: int(x))
    
    # external_id = 'nanoHUB_user_ID__c'
    # object_id = 'Contact'
    
    # db_temp = DB2SalesforceAPI(sf_login_params)
    
    # db_temp.external_id = external_id
    # db_temp.object_id = object_id
    
    # temp_sample = temp_sample.drop(columns=\
        # ['FirstName','LastName','Domain__c','org_name','Active_duration__c','Email']) #
    
    # db_temp.send_data(temp_sample)
    
    # time.sleep(np.random.randint(2,10))
    # db_temp.check_bulk_status()

    #db_temp.check_bulk_failed_results()
    
    ###
    # logging.basicConfig(filename=cwd+'/logging/batch_'+str(batch_no)+'.log', \
    #     encoding='utf-8', level=logging.DEBUG)
    # logging.debug('Logging file header: \n')
    
    # logging.debug('the people: '+';'.join(fullnames))

    # # gs logging
    # logging.debug('google scholar: ' + ';'.join(temp_sample['Google_Scholar_ID_sf__c']))

    # # orcid logging
    # logging.debug('ORCID: '+ ';'.join(temp_sample['ORCID_sf__c']))
    
    # # research ID logging
    # logging.debug('research ID: ' + ';'.join(temp_sample['Research_ID_sf__c']))
    
    # # research gate logging
    # logging.debug('research gate ID: ' + ';'.join(temp_sample['ResearchGate_ID_sf__c']))    
    
    
    # save this current batch results
    try:
        os.mkdir(cwd+'/scrape_results')
    except:
        print('directory exists - ignore this message')
    
    # temp_sample.to_csv(cwd+'/scrape_results/batch_result_'+str(batch_no))
    
    ## build SF profile links
    temp_sample['sf_urls'] = ['https://na172.lightning.force.com/lightning/r/Contact/{}/view'.format(i) \
            for i in temp_sample['Id'].to_list()]
    
    temp_sample['gk_pls_check'] = -1
    temp_sample['gscholar_check'] = -1
    temp_sample['ORCID_check'] = -1
    temp_sample['rs_gate_check'] = -1
    
    temp_sample.to_excel(cwd+'/scrape_results/batch_results_'+str(batch_no)+'.xlsx')
    
    ## validated checkbox; g_pls_verify
    
    batch_no += 1
    
    # wait for next batch instance
    time.sleep(np.random.randint(30,121))

    if start_t - time.time() >= 3*60*60: #3 hour run sessions
        break
# %% graveyard
    
    # %% Research ID_sf
    ## Do the same thing as ORCID ID search
    # rather than web of science researcherID - use publons as the filter
    
    # wos_researchers = [] #web of science researcherIDs
        
    # # populate researcherIDs
    # for i in fullnames:
    #     temp_name = i.split(' ')
    #     test = search('{} {} publons'.format(temp_name[0],temp_name[-1]),tld='com', lang='en', \
    #                   num=5, start=0, stop=5, pause=np.random.randint(2,5))
    #     list_test = [j for j in test]
    #     if len(list_test) == 0:
    #         wos_researchers.append('')
    #     else:
    #         for ind,j in enumerate(list_test):
    #             wos_matches = re.findall(r'publons.com/researcher/\d+',j)
    #             if len(wos_matches) > 0:
    #                 # take the first match and move on
    #                 temp_url = 'https://{}/{}-{}'.format(wos_matches[0],temp_name[0],temp_name[-1])
    #                 wos_researchers.append(temp_url)
    #                 break
    
    #             if ind == len(list_test)-1:
    #                 wos_researchers.append('')
    #                 break
                
    # temp_sample['Research_ID_sf__c'] = wos_researchers
    # time.sleep(np.random.randint(2,10))
    
    # %% SCOPUS - can't find results, blanked out for now
    



