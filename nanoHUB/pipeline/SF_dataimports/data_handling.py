import pandas as pd
from copy import deepcopy
from nanoHUB.logger import logger


def split_names(idf: pd.DataFrame) -> [pd.DataFrame, bool]:
    try:
        names = idf['Name'].to_list()

        fname = deepcopy(names)
        lname = deepcopy(names)
        for ind, val in enumerate(names):
            val = val.split(' ')
            fname[ind] = val[-1]
            lname[ind] = val[0]

        idf['firstname'] = fname
        idf['lastname'] = lname
        name_flag = True
    except:
        name_flag = False

    return [idf, name_flag]


def filter_bad_emails(idf: pd.DataFrame, log: logger) -> pd.DataFrame:
    #email check rows
    grows = []
    brows = []
    for ind,val in enumerate(idf['Email'].to_list()):
        if '@' in val:
            grows.append(ind)
        else:
            brows.append(ind)
    idf = idf.iloc[grows,:].reset_index().iloc[:,1:]

    log.info("Number of good emails found: %d" %len(grows))
    log.info("Number of bad emails found: %d" % len(brows))

    return idf


def strip_spaces_cols(idf: pd.DataFrame) -> pd.DataFrame:
    prev_idf_cols = idf.columns
    idf_cols = [i.strip() for i in idf.columns]
    idf.columns = idf.columns.str.strip()
    idf = idf.rename(columns={j:idf_cols[i] for i,j in enumerate(prev_idf_cols)})

    return idf


def rename_columns(idf: pd.DataFrame) -> pd.DataFrame:
    idf = idf.rename(columns={'email':'Email','EMAIL':'Email','E-mail Address':'Email', \
                              'Email Address':'Email','Recipient Email':'Email'})
    idf = idf.rename(columns={'First Name':'firstname','Last Name':'lastname','FirstName':'firstname','LastName':'lastname'})

    idf = idf.rename(columns={0:'Email'})

    return idf


def add_venue(idf: pd.DataFrame, ) -> pd.DataFrame:
    # import_as =
    if 'Venue__c' in idf.columns:
        idf["Venue__c"] = idf["Venue__c"] + ';' + idf["Import as Venue__c"]
        
    return idf