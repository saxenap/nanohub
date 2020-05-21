import pandas as pd
import sqlalchemy as sql

input_df = pd.read_csv('./7mm_companies.csv')

sql_login_params = {"username": "invalid", "password": "invalid"}

engine = sql.create_engine('mysql+pymysql://%s:%s@127.0.0.1/wang159_myrmekes?charset=utf8mb4'%(sql_login_params['username'], sql_login_params['password']))
input_df.to_sql('companies_email_domain', con=engine, if_exists='replace', chunksize=200000)
