import sys

import code
import os
from pprint import pprint, pformat
import logging

from glob import glob
import re
import datetime

import pandas as pd

import sqlalchemy as db
from sqlalchemy import *
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.ext.declarative import declarative_base
from nanoHUB.application import Application

Base = declarative_base()
from sqlalchemy.orm import sessionmaker
import time


def save_data_from_db_to_df(inparams, db_name, sql_table, date_range=False):
    # transfer table data from SQL DB to dataframe
    if inparams.CI:
        # CI/Testing: find the correct Feather and move it to staging directory
        expected_feather_filepath = os.path.join(inparams.CI_dir, 'data', 'cleaned_' + sql_table.name + '.feather')

        logging.info('Loading data from CI samples: ' + expected_feather_filepath)

        df = pd.read_feather(expected_feather_filepath)

    else:
        # Production: connect with live DB
        start_time = time.time()

        application = Application.get_instance()
        db_engine = application.new_db_engine(db_name)

        sql_select = db.select([sql_table])
        if date_range:
            sql_select = sql_select.where(and_(
                sql_table.c.datetime >= (inparams.class_probe_range[0] + ' 00:00:00'), sql_table.c.datetime <= (
                            inparams.class_probe_range[1] + ' 23:59:59')))

        logging.info("Retrieving data from %s.%s range: %s - %s" % (
            db_name,
            sql_table.name,
            inparams.class_probe_range[0],
            inparams.class_probe_range[1]
        ))
        # load table into DF
        df = pd.read_sql(sql_select, db_engine)

        # remove uncastable rows from df, so we can save them as Feathers
        # for example, datetime in form of "0000-00-00 00:00:00" cannot be recognized as datetime

        for this_column in sql_table.columns:
        # for each column in sql table as declared

            this_column_python_type = this_column.type.python_type

        # remove all rows should be of type datetime, but recorded as str
        if this_column_python_type == datetime.datetime:
            df = df.drop(df[df[this_column.name].apply(lambda x: type(x) == str)].index)
        end_time = time.time()
        print("DB time:", end_time - start_time)

        # save DF using Feather
        df.reset_index(drop=True).to_feather(
            os.path.join(inparams.scratch_dir, inparams.class_probe_range[0] + '_' + inparams.class_probe_range[1] + '/' + sql_table.name + '.feather')
        )

        # display a small part of DF
        logging.debug(df)

    return


def gather_data(inparams):
    ### Save SQL tables into Feather

    # TABLE
    sql_table = db.Table('jos_tool_version', db.MetaData(),
                         db.Column('toolname', db.String(120)),
                         db.Column('instance', db.String(120)),
                         )

    save_data_from_db_to_df(inparams, 'nanohub', sql_table)

    # TABLE
    '''
    +-----------------+--------------+------+-----+---------------------+----------------+
    | Field           | Type         | Null | Key | Default             | Extra          |
    +-----------------+--------------+------+-----+---------------------+----------------+
    | id              | bigint(20)   | NO   | PRI | NULL                | auto_increment |
    | sessionid       | bigint(20)   | NO   | MUL | 0                   |                |
    | datetime        | datetime     | NO   | MUL | 0000-00-00 00:00:00 |                |
    | orgtype         | tinyint(4)   | NO   | MUL | 0                   |                |
    | countryresident | char(2)      | NO   | MUL |                     |                |
    | countrycitizen  | char(2)      | NO   | MUL |                     |                |
    | protocol        | tinyint(4)   | NO   | MUL | 0                   |                |
    | success         | tinyint(4)   | NO   | MUL | 0                   |                |
    | countryip       | char(2)      | NO   | MUL |                     |                |
    | ip              | tinytext     | NO   | MUL | NULL                |                |
    | host            | tinytext     | NO   |     | NULL                |                |
    | user            | tinytext     | NO   | MUL | NULL                |                |
    | tool            | varchar(120) | NO   | MUL |                     |                |
    | pid             | int(11)      | YES  |     | NULL                |                |
    | domain          | varchar(64)  | NO   |     |                     |                |
    | filesystem      | tinytext     | YES  |     | NULL                |                |
    | execunit        | tinytext     | YES  |     | NULL                |                |
    | walltime        | int(11)      | NO   |     | -1                  |                |
    | cputime         | int(11)      | NO   |     | -1                  |                |
    | error           | tinytext     | YES  |     | NULL                |                |
    +-----------------+--------------+------+-----+---------------------+----------------+
    '''

    sql_table = db.Table('toolstart', db.MetaData(),
                         db.Column('datetime', db.DateTime),
                         db.Column('user', db.String(120)),
                         db.Column('tool', db.String(120)),
                         db.Column('ip', db.String(120)),
                         db.Column('protocol', db.String(120))
                         )

    save_data_from_db_to_df(inparams, 'nanohub_metrics', sql_table, date_range=True)

    # TABLE
    '''
    +---------------+--------------+------+-----+---------+----------------+
    | Field         | Type         | Null | Key | Default | Extra          |
    +---------------+--------------+------+-----+---------+----------------+
    | id            | int(11)      | NO   | PRI | NULL    | auto_increment |
    | name          | varchar(255) | NO   | MUL |         |                |
    | username      | varchar(150) | NO   | UNI | NULL    |                |
    | email         | varchar(100) | NO   | MUL |         |                |
    | usertype      | varchar(25)  | NO   | MUL |         |                |
    | block         | tinyint(4)   | NO   | MUL | 0       |                |
    | approved      | tinyint(4)   | NO   |     | 2       |                |
    | sendEmail     | tinyint(4)   | YES  |     | 0       |                |
    | registerDate  | datetime     | YES  |     | NULL    |                |
    | lastvisitDate | datetime     | YES  |     | NULL    |                |
    | activation    | int(11)      | NO   |     | 0       |                |
    | params        | text         | NO   |     | NULL    |                |
    | lastResetTime | datetime     | YES  |     | NULL    |                |
    | resetCount    | int(11)      | NO   |     | 0       |                |
    +---------------+--------------+------+-----+---------+----------------+
    '''

    sql_table = db.Table('jos_users', db.MetaData(),
                         db.Column('id', db.Integer),
                         db.Column('name', db.String(120)),
                         db.Column('username', db.String(120)),
                         db.Column('email', db.String(120)),

                         )

    save_data_from_db_to_df(inparams, 'nanohub', sql_table)
