# Created by saxenap at 6/23/22
import json
import logging
from dataclasses import dataclass
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import time
from pathlib import Path
from dotenv import load_dotenv
from nanoHUB.application import Application
from nanoHUB.dataaccess.lake import create_default_s3mapper, S3FileMapper
import os
import pandas as pd
from nanoHUB.infrastructure.eventing import EventNotifier, IEvent, IEventHandler
from nanoHUB.command import ICommandHandler, ICommand
from requests.exceptions import ConnectionError
from nanoHUB.infrastructure.salesforce.client import ISalesforceFactory
from nanoHUB.infrastructure.salesforce.query import SalesforceObject
from nanoHUB.configuration import DataLakeConfiguration, SalesforceBackupConfiguration
from nanoHUB.logger import get_app_logger


cwd = os.getcwd()
load_dotenv()

now = time.strftime("%Y%m%d-%H%M%S")
backup_folder = 'salesforce_backups' + '/' + now
print("Commencing backup.")
print("Time is %s", now)

datadir = os.environ['APP_DIR'] + '/' + backup_folder
print('Saving Results -> Local dir: ' + datadir)

datapath = Path(datadir)
try:
    datapath.mkdir(parents=True) #in python 3.5 we can switch to using  exist_ok=True
except FileExistsError:
    pass


class SalesForceBackupCommand(ICommand):
    specific_fields: [] = []
    number_of_retries: int = 6
    name: str = 'BackupCommand'

    def get_name(self) -> str:
        return self.name

    def __repr__(self):
        return 'SalesForceBackupCommand(number_of_retries = ' + str(self.number_of_retries) + \
               'name = ' + self.get_name() + \
                'specific_fields = ' + ','.join(self.specific_fields) + \
                ')'

    def __str__(self):
        return json.dumps({
            'name': self.name,
            'number_of_retries': self.number_of_retries,
            'specific_fields': self.specific_fields
        })


@dataclass
class BackupFinishedEvent(IEvent):
    df: dict
    object_name: str
    event_name: str = 'BackupFinishedEvent'

    def get_event_name(self) -> str:
        return self.event_name

    def get_dict(self) -> dict:
        return self.df

    def get_object_name(self) -> str:
        return self.object_name


class SalesforceBackup(ICommandHandler):
    backup_finished: str = 'BackupFinished'

    def __init__(
            self, client_factory: ISalesforceFactory, notifier: EventNotifier, logger: logging.Logger
    ):
        self.client_factory = client_factory
        self.notifier = notifier
        self.logger = logger

    def handle(self, command) -> None:
        client = self.client_factory.create_new()
        sf_object = self.create_new_sf_object()
        description = client.describe()
        names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]
        for name in names:
            count = 1
            while count < command.number_of_retries + 1:
                try:
                    self.logger.info("Attempt #%d for object %s" %(count, name))
                    df = sf_object.get_records_for(name)
                    self.logger.debug("Dataframe for %s" % name)
                    self.logger.debug(df.iloc[:5].to_json)
                    self.logger.info("Attempt Successful. Rows obtained: %d" % len(df))
                    count = 7
                    self.notifier.notify_for(BackupFinishedEvent(df.to_dict(), name))
                except SalesforceMalformedRequest as e:
                    count = count + 1
                    sf_object = self.create_new_sf_object()
                    self.logger.info("Malformed Request: Retrying.")
                    continue
                except ConnectionError as ce:
                    count = count + 1
                    sf_object = self.create_new_sf_object()
                    self.logger.info("Connection Error: Retrying.")
                    continue

    def create_new_sf_object(self) -> SalesforceObject:
        client = self.client_factory.create_new()
        return SalesforceObject(client)


class SalesforceBackupGeddes(IEventHandler):
    def __init__(
            self, mapper: S3FileMapper, file_path: str, logger: logging.Logger
    ):
        self.mapper = mapper
        self.file_path = file_path
        self.logger = logger

    def handle(self, event: BackupFinishedEvent):
        object_name = event.get_object_name()
        file_path = self.file_path + '/' + object_name + '.csv'
        df = pd.from_dict(event.get_dict())
        self.mapper.save_as_csv(
            df, file_path, index=None
        )
        self.logger.info("%d records for object %s saved at: %s" % (len(df), object_name, file_path))


print('Backup completed!')
print('Path %s' % backup_folder)


class DefaultBackupCommandHandler:
    def create_new(
            self, application: Application, client_factory: ISalesforceFactory, loglevel: str = 'INFO'
    ) -> SalesforceBackup:
        logger = get_app_logger('SalesforceBackups', loglevel)

        notifier = EventNotifier(SalesforceBackupGeddes(
                create_default_s3mapper(application, SalesforceBackupConfiguration.bucket_name_raw),
                SalesforceBackupConfiguration.geddes_folder_path,
                logger
            )
        )

        return SalesforceBackup(client_factory, notifier, logger)



