# -*- coding: utf-8 -*-
"""
Created on Thu Oct  8 16:09:14 2020

@author: henry
"""
import argparse
import numpy as np
import pandas as pd
import os
from DB2SalesforceAPI import DB2SalesforceAPI

sql_login_params = {"username": "wang2506_ro", "password": "fnVnwcCS7iT45EsA"}
sf_login_params = {
    "grant_type": "password",
    "client_id": "3MVG95jctIhbyCppj0SNJ75IsZ1y8UPGZtSNF4j8FNVXz.De8Lu4jHm3rjRosAtsHy6qjHx3i4S_QbQzvBePG",
    "client_secret": "D1623C6D3607D4FC8004B92C761DFB6C1F70CCD129C5501E357028DFA00F5764",
    "username":"wang2506@purdue.edu",
    "password":"shit9927289sSYTkLiGvyK2UrazHFmjFUGU",
}
cwd = os.getcwd()

# %% argparse
parser = argparse.ArgumentParser()

# adding the arguments
parser.add_argument('-fn','--file_name',help='specify the file name with extension') #default string
parser.add_argument('-ft','--file_type',help='specify the extension, no period, e.g., csv, xlsx, etc.')
parser.add_argument('-s','--style',help='the style of SF import, e.g., contact, lead, org, etc.')

parser.add_argument('-c','--contact',help='import contact',action='store_true')
parser.add_argument('-l','--lead',help='import leads',action='store_true')


# these are optional - specify which entries are active
parser.add_argument('-v','--venue',help='venue flag',action='store_true')

args = parser.parse_args()

# %% contact import
def contact_import(args):
    if type(args.file_type) == str:
        f_type = args.file_type
    else:
        f_type = args.file_name.split('.')[-1]
    
    if f_type == 'csv':
        idf = pd.read_csv(args.file_name)
    elif f_type == 'xlsx':
        idf = pd.read_excel(args.file_name,sheet_name=0,header=0)
    
    print(idf.head(2))
    
    # rename email column if needed
    if 'Email' not in idf.columns:
        #find the nearest 'Email' related column name
        #do levenshtein distance later
        idf = idf.rename(columns={'email':'Email'})

    # rename names to either firstname lastname Middle_name__c if needed (Name)
    if 'Name' not in idf.columns or 'firstname' not in idf.columns:
        #check the others
        if 'First Name' in idf.columns:
            idf = idf.rename(columns={'First Name':'firstname','Last Name':'lastname'})
        
    # sequential columns check
    if args.venue == True:
        #rename engagement venue to Venue__c
        idf = idf.rename(columns={'Engagement Venue':'Venue__c'})

    # email check rows
    grows = []
    brows = []
    for ind,val in enumerate(idf['Email'].to_list()):
        if '@' in val:
            grows.append(ind)
        else:
            brows.append(ind)
    
    idf = idf.iloc[grows,:].reset_index().iloc[:,1:]
    
    print(idf.head(2))
    
    # salesforce queries for contact data
    db_s = DB2SalesforceAPI(sf_login_params)
    sf_df = db_s.query_data('SELECT nanoHUB_user_ID__c, Email, Venue__c FROM Contact')
    
    # find all existing contacts
    sf_emails = sf_df['Email'].to_list()
    grows = []
    brows = [] #dont need the sf_bad_rows as send to leads
    sf_grows = []
    for ind,val in enumerate(idf['Email'].to_list()):
        if val in sf_emails:
            grows.append(ind)
            sf_grows.append(sf_emails.index(val))
        else:
            brows.append(ind)
    
    # pull the matching SF entries and the matching import df entries
    sf_df_match = sf_df.iloc[sf_grows,:].reset_index().iloc[:,1:]
    idf_match = idf.iloc[grows,:].reset_index().iloc[:,1:]
    lead_df = idf.iloc[brows,:].reset_index().iloc[:,1:]
    
    print(sf_df_match.head(2))
    print(idf_match.head(2))
    
    # linear join since the sequence is matching
    for ind,val in enumerate(sf_df_match['Venue__c']):
        try:
            val = val.split(';')
            print(val)
            val.append(idf['Venue__c'][ind])
            val = ';'.join(val)
        except:
            val = idf['Venue__c'][ind]
        
        sf_df_match['Venue__c'][ind] = val
    
    print(sf_df_match.head(5))
    
    # rebuild api object
    db_s_c = DB2SalesforceAPI(sf_login_params)
    
    # send data to SF
    db_s_c.object_id = 'Contact'
    db_s_c.external_id = 'nanoHUB_user_ID__c'
    
    db_s_c.send_data(sf_df_match)

    return lead_df
    
# %% lead import
def lead_import(args,lead_df=None):
    db_s = DB2SalesforceAPI(sf_login_params)
    sf_df = db_s.query_data('SELECT Email, Venue__c, SF_indexer__c FROM Lead')
    
    # find the max sf_indexer
    indexers = sf_df['SF_indexer__c'].fillna(0).to_list()
    max_ind = max(indexers)
    
    # find all existing leads
    sf_emails = sf_df['Email'].to_list()
    m_rows = []
    nm_rows = [] #don't need sf no match rows
    sf_mrows = []
    
    for ind,val in enumerate(lead_df['Email'].to_list()):
        if val in sf_emails:
            m_rows.append(ind)
            sf_mrows.append(sf_emails.index(val))
        else:
            nm_rows.append(ind)
    
    # filter the matches
    sf_df_match = sf_df.iloc[sf_mrows,:].reset_index().iloc[:,1:]
    join_idf = lead_df.iloc[m_rows,:].reset_index().iloc[:,1:]
    new_idf = lead_df.iloc[nm_rows,:].reset_index().iloc[:,1:]
    
    # join the existing salesforce leads with the new leads
    print(sf_df_match.head(2))
    print(join_idf.head(2))
    
    # linear join since the sequence is matching
    for ind,val in enumerate(sf_df_match['Venue__c']):
        try:
            val = val.split(';')
            print(val)
            val.append(join_idf['Venue__c'][ind])
            val = ';'.join(val)
        except:
            val = join_idf['Venue__c'][ind]
        
        sf_df_match['Venue__c'][ind] = val    
    
    print(sf_df_match.head(5))
    
    # assign new SF_indexers for the new leads
    new_max_ind = max_ind+new_idf.shape[0]
    # print(new_idf.shape)
    # print(max_ind)
    # print(new_max_ind)
    new_idf['SF_indexer__c'] = np.arange(max_ind+1,new_max_ind+1,step=1)
    
    #send the matching ones
    db_s_l1 = DB2SalesforceAPI(sf_login_params)
    
    # send data to SF
    db_s_l1.object_id = 'Lead'
    db_s_l1.external_id = 'SF_indexer__c'
    
    db_s_l1.send_data(sf_df_match)
    
    #send the new ones
    db_s_l2 = DB2SalesforceAPI(sf_login_params)
    
    # send data to SF
    db_s_l2.object_id = 'Lead'
    db_s_l2.external_id = 'SF_indexer__c'
    
    db_s_l2.send_data(new_idf)
    
    return True

    
# %% determine the file style
if args.contact == True and args.lead == True:
    lead_df = contact_import(args=args)
    print(lead_df.head(2))
    lead_import(args=args,lead_df=lead_df)
















