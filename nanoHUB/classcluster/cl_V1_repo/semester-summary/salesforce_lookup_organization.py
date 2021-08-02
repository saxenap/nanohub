def lookup_user_organizations():
    from DB2SalesforceAPI import DB2SalesforceAPI
    import pandas as pd

    sf_login_params = {
        "grant_type": "password",
        "client_id": "3MVG95jctIhbyCppj0SNJ75IsZ1y8UPGZtSNF4j8FNVXz.De8Lu4jHm3rjRosAtsHy6qjHx3i4S_QbQzvBePG",
        "client_secret": "D1623C6D3607D4FC8004B92C761DFB6C1F70CCD129C5501E357028DFA00F5764",
        "username": "wang2506@purdue.edu",
        "password": "npass2021HDfJLhBGDx11xWCKlEbHQKhF",
    }
    # create DB2 to Salesforce API object
    db_s = DB2SalesforceAPI(sf_login_params)

    # get username and their Salesforce organizations ID
    sf_username_df = pd.DataFrame(db_s.query_data("select nanoHUB_username__c, Organization_composite__c from Contact"))
    print(sf_username_df.head(5))
    # get Salesforce ID for organizations
    sf_org_name_df = db_s.query_data("select Id, Name from organization__c")
    print(sf_org_name_df.head(5))

    pd.set_option('display.max_columns', None)
    merged_df = pd.merge(left=sf_username_df, right=sf_org_name_df, how='left', left_on='Organization_composite__c',
                           right_on='Id')
    merged_df = merged_df.drop(columns=['Id','Organization_composite__c'])
    print(merged_df)
    print(merged_df.size)
    return merged_df