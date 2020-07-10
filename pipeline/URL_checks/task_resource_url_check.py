# Checks URL validity for nanoHUB resources' descriptions
import argparse
import pandas as pd

import sqlalchemy as sql

from bs4 import BeautifulSoup

from tqdm import tqdm
tqdm.pandas()

import requests


import ipdb

from pprint import pprint


class NanoHUB_SE:
  def __init__(self, inparams):

    # login-related parameters
    self.inparams = inparams

    # results (invalid only)
    self.results = list()


  def get_db2(self, sql_query):

    engine = sql.create_engine('mysql+pymysql://%s:%s@%s' \
                                                   %(self.inparams.SQL_username, self.inparams.SQL_password, self.inparams.SQL_addr))

    return pd.read_sql_query(sql_query, engine)

  def to_db2(self):

    #
    # Saving results to SQL server
    #
    db_engine = sql.create_engine('mysql+pymysql://'+self.inparams.SQL_username+':'+self.inparams.SQL_password \
                                             +'@'+self.inparams.SQL_addr+':'+self.inparams.SQL_port+'/wang159_myrmekes')  

    pd.DataFrame(self.results, columns=['resource_ID', 'href', 'href_text', 'status'])\
                                  .to_sql('issue_invalid_urls', con=db_engine, if_exists='replace')

    return


  def add_result(self, page_url, invalid_url, invalid_url_text, invalid_code):
    # insert a result into self.results

    self.results.append(['%s'%page_url, '%s'%invalid_url, '%s'%invalid_url_text, '%s'%invalid_code])

    return



  def check_html(self, this_row):

    def get_addr(a_href):
      # get a valid http address

      a_href = a_href.strip('/')

      if len(a_href) < 1:
        # homepage
        return 'https://nanohub.org'

      # '/site/file/1234' -> '/app/site/file/1234'
      if a_href.startswith('site/'):
          return 'https://nanohub.org/app/'+a_href

      if a_href.startswith('https'):
          return a_href

      if a_href.startswith('http'):
          # NOT "http"
          return 'http'+a_href[4:]

      if '.' in a_href.split('/')[0]:
        # starts with "xyz.a", possible absolute address
        # "amazon.com"
        return 'https://'+a_href


      return 'https://nanohub.org/'+a_href




    this_id = this_row.id
    this_html = this_row.fulltxt

    # create soup
    soup = BeautifulSoup(this_html, 'html.parser')

    # check all href
    for a in soup.find_all('a', href=True):
      a_href = a['href'].encode('utf-8').decode('unicode_escape').replace('"', '').replace("'", '').replace('\\', '')
      a_text = a.get_text()

      # get absolute HTTP address
      http_addr = get_addr(a_href)

      # test URL connection
      try:
        #print(this_id)
        #print(http_addr)
        r = requests.get(http_addr, timeout=10, headers={"User-Agent":"Mozilla/5.0"})

      except requests.exceptions.SSLError as e:

        self.add_result(this_id, a_href, a_text, 'Valid URL, but certificate verification failed.')
        continue

      except requests.exceptions.ConnectionError as e:

        self.add_result(this_id, a_href, a_text, 'Connection error.')
        continue

      except:

        self.add_result(this_id, a_href, a_text, 'Invalid URL.')
        continue

      # Connect-ble URLs
      if not r.ok:
        self.add_result(this_id, a_href, a_text, r.status_code)






  def check_resources(self):
    # start check for URLs in resource pages

    # obtain data from DB2 SQL
    sql_query = 'select id, fulltxt from nanohub.jos_resources where published=1 and standalone=1'
    #sql_query = 'select id, fulltxt from nanohub.jos_resources where published=1 and standalone=1 limit 10'

    resource_df = self.get_db2(sql_query)

    # start check
    resource_df.progress_apply(self.check_html, axis=1)






if __name__ =='__main__':
  parser = argparse.ArgumentParser(description='nanoHUB URL checker for URLs in resource pages')

  # SQL connection
  parser.add_argument('--SQL_username', help='SQL database username', 
                                   action='store', default='wang2506_ro')
  parser.add_argument('--SQL_password', help='SQL password', 
                                   action='store', default='fnVnwcCS7iT45EsA')
  parser.add_argument('--SQL_addr', help='SQL address', 
                                   action='store', default='127.0.0.1')
  parser.add_argument('--SQL_port', help='SQL port', 
                                   action='store', default='3306')
                                          
  inparams = parser.parse_args()

  # Create a search object
  nanoHUB_SE = NanoHUB_SE(inparams)

  # start check
  nanoHUB_SE.check_resources()

  # save results to DB2
  nanoHUB_SE.to_db2()