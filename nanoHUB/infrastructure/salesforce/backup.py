# Created by saxenap at 6/23/22
import json
import logging
from dataclasses import dataclass
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import time
from nanoHUB.application import Application
from nanoHUB.dataaccess.lake import create_default_s3mapper, S3FileMapper
import pandas as pd
from nanoHUB.infrastructure.eventing import EventNotifier, IEvent, IEventHandler
from nanoHUB.command import (
    ICommandHandler,
    ICommand,
    MetricsReporterDecorator,
    InitialExecutionDecorator,
    TimingProfileReporter,
    MemoryProfileReporter,
    NullCommandHandler
)
from requests.exceptions import ConnectionError
from nanoHUB.infrastructure.salesforce.client import ISalesforceFactory
from nanoHUB.infrastructure.salesforce.query import SalesforceObject
from nanoHUB.configuration import SalesforceBackupConfiguration
from nanoHUB.logger import get_app_logger
from datetime import datetime
from nanoHUB.utilities.display import ColorOutput
# cwd = os.getcwd()
#
# now = time.strftime("%Y%m%d-%H%M%S")
# backup_folder = 'salesforce_backups' + '/' + now
# print("Commencing backup.")
# print("Time is %s", now)
#
# datadir = os.environ['APP_DIR'] + '/' + backup_folder
# print('Saving Results -> Local dir: ' + datadir)
#
# datapath = Path(datadir)
# try:
#     datapath.mkdir(parents=True) #in python 3.5 we can switch to using  exist_ok=True
# except FileExistsError:
#     pass


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

    def __repr__(self):
        return 'BackupFinishedEvent(object_name = ' + self.get_object_name() + ', df = ' + str(self.df) + ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'object_name': self.get_object_name(),
            'dataframe_dict': self.df
        })


class SalesforceBackup(ICommandHandler):
    backup_finished: str = 'BackupFinished'

    def __init__(
            self, client: Salesforce, notifier: EventNotifier, logger: logging.Logger
    ):
        self.client = client
        self.notifier = notifier
        self.logger = logger

    def handle(self, command: SalesForceBackupCommand) -> None:
        self.logger.info('Salesforce backup started.')
        sf_object = SalesforceObject(self.client)
        description = self.client.describe()
        names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]
        for name in names:
            count = 1
            while count < command.number_of_retries + 1:
                try:
                    self.logger.debug("Attempt #%d for object %s" %(count, name))
                    df = sf_object.get_records_for(name)
                    self.logger.debug("Dataframe for %s" % name)
                    self.logger.debug(df.iloc[:5].to_json)
                    self.logger.debug("Attempt Successful. Rows obtained: %d" % len(df))
                    count = command.number_of_retries
                    event = BackupFinishedEvent(df.to_dict(), name)
                    event.event_datetime = command.get_datetime()
                    self.notifier.notify_for(event)
                    break
                except SalesforceMalformedRequest as e:
                    count = count + 1
                    self.logger.debug("Malformed Request: Retrying.")
                    continue
                except ConnectionError as ce:
                    count = count + 1
                    self.logger.debug("Connection Error: Retrying.")
                    continue
        self.logger.info('Salesforce backup finished.')

    def get_name(self) -> str:
        return 'SalesforceBackup'


class SalesforceBackupGeddes(IEventHandler):
    def __init__(
            self, mapper: S3FileMapper, file_path: str, logger: logging.Logger
    ):
        self.mapper = mapper
        self.logger = logger
        self.file_path = file_path

    def handle(self, event: BackupFinishedEvent):
        object_name = event.get_object_name()
        event_dt = datetime.strptime(event.get_event_datetime(), "%Y%m%d-%H%M%S")
        file_path = self.file_path + '/' + \
                    str(event_dt.year) + '/' +\
                    str(event_dt.month) + '/' + \
                    str(event_dt.day) + '/' + \
                    event_dt.strftime("%Y%m%d-%H%M%S") + '/' + \
                    object_name + '.csv'
        df = pd.DataFrame(event.get_dict())
        self.mapper.save_as_csv(
            df, file_path, index=None
        )
        self.logger.info(
            "%s %s: %s %d records saved in Geddes at %s" % (
                ColorOutput.BOLD, event.get_object_name(), ColorOutput.END, len(df), file_path
            )
        )


class SalesforceBackupResultLogger(IEventHandler):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle(self, event: BackupFinishedEvent):
        self.logger.info(
             "%s %s %s backed up." % (ColorOutput.BOLD, event.get_object_name(), ColorOutput.END)
        )
        self.logger.debug(
            "%s: %s." % (event.get_object_name(), event.__str__())
        )


class DefaultBackupCommandHandler:
    def create_new(
            self, application: Application, client_factory: ISalesforceFactory, loglevel: str = 'INFO'
    ) -> ICommandHandler:
        logger = get_app_logger('SalesforceBackups', loglevel)

        notifier = EventNotifier()
        notifier.add_event_handler(SalesforceBackupGeddes(
            create_default_s3mapper(application, SalesforceBackupConfiguration.bucket_name_raw),
            SalesforceBackupConfiguration.geddes_folder_path,
            logger
        ))
        notifier.add_event_handler(SalesforceBackupResultLogger(logger))
        return MetricsReporterDecorator(
            InitialExecutionDecorator(
                SalesforceBackup(client_factory.create_new(), notifier, logger), logger
            ), [TimingProfileReporter(), MemoryProfileReporter()], logger
        )



