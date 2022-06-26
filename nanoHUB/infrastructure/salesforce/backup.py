# Created by saxenap at 6/23/22
import json
import logging
from dataclasses import dataclass
from simple_salesforce import Salesforce, SalesforceMalformedRequest
import time
from nanoHUB.application import Application
from nanoHUB.dataaccess.lake import create_default_s3mapper, S3FileMapper
import pandas as pd
from nanoHUB.infrastructure.eventing import (
    EventNotifier, IEvent, IEventHandler, IFilePathProvider, FilePathByDatetime
)
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
class SFBackupStartedEvent(IEvent):
    backup_started_datetime: str
    event_name: str = 'SFBackupStartedEvent'

    def __init__(self, started_datetime: str):
        self.backup_started_datetime = started_datetime
        IEvent.__init__(self)

    def get_backup_started_datetime(self) -> str:
        return self.backup_started_datetime

    def __repr__(self):
        return 'SFRecordObtainedEvent()'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name()
        })


@dataclass
class SFBackupFinishedEvent(IEvent):
    record_names: []
    backup_finished_datetime: str
    event_name: str = 'SFBackupFinishedEvent'

    def __init__(self, record_names: [], finished_datetime: str):
        self.record_names = record_names
        self.backup_finished_datetime = datetime.strptime(finished_datetime, "%Y%m%d-%H%M%S").ctime()
        IEvent.__init__(self)

    def get_record_names(self) -> []:
        return self.record_names

    def get_backup_finished_datetime(self) -> str:
        return self.backup_finished_datetime

    def __repr__(self):
        return 'SFRecordObtainedEvent(record_names = ' + str(self.get_record_names()) + ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'record_names': self.get_record_names()
        })

@dataclass
class SFRecordObtainedEvent(IEvent):
    object_name: str
    object_data: dict
    number_of_records: int
    command_datetime: str
    event_name: str = 'SFRecordObtainedEvent'

    def __init__(self, object_name: str, object_data: dict, number_of_records: int, command_datetime: str):
        self.object_data = object_data
        self.object_name = object_name
        self.number_of_records = number_of_records
        self.command_datetime = command_datetime
        IEvent.__init__(self)

    def get_event_name(self) -> str:
        return self.event_name

    def get_object_data(self) -> dict:
        return self.object_data

    def get_number_of_records(self) -> int:
        return self.number_of_records

    def get_object_name(self) -> str:
        return self.object_name

    def get_command_datetime(self) -> str:
        return self.command_datetime

    def __repr__(self):
        return 'SFRecordObtainedEvent(object_name = ' + self.get_object_name() + ', object_data = ' + str(self.get_object_data()) + ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'object_name': self.get_object_name(),
            'object_data': self.get_object_data(),
            'number_of_records': self.get_number_of_records()
        })


class ProblemObtainingObjectRecords(RuntimeError):
    def __init__(self, message, object_name: str):
        self.message = "%s - Problem obtaining records (Original message: %s)" % (object_name, message)
        self.object_name = object_name

    def get_object_name(self) -> str:
        return self.object_name


class ISFObjectRecordProvider:
    def provide_for(self, object_name: str) -> pd.DataFrame:
        raise NotImplementedError


class SFObjectRecordsLoggerProvider(ISFObjectRecordProvider):
    def __init__(
            self,
            inner_provider: ISFObjectRecordProvider,
            logger: logging.Logger
    ):
        self.inner_provider = inner_provider
        self.logger = logger

    def provide_for(self, object_name: str) -> pd.DataFrame:
        df = pd.DataFrame()
        try:
            self.logger.debug("%s%s%s - Attempting to query now." % (ColorOutput.BOLD, object_name, ColorOutput.END))
            df = self.inner_provider.provide_for(object_name)
        except ProblemObtainingObjectRecords as e:
            self.logger.debug(e.message)
            raise e
        return df


class SFObjectRecordRetriesProvider(ISFObjectRecordProvider):
    def __init__(
            self,
            inner_provider: ISFObjectRecordProvider,
            number_of_retries:int,
            logger: logging.Logger
    ):
        self.inner_provider = inner_provider
        self.number_of_retries = number_of_retries
        self.logger = logger

    def provide_for(self, object_name: str) -> pd.DataFrame:
        count = 1
        df = pd.DataFrame()
        while count < self.number_of_retries + 1:
            try:
                df = self.inner_provider.provide_for(object_name)
                break
            except ProblemObtainingObjectRecords as e:
                count = count + 1
                if count == self.number_of_retries + 1:
                    raise e
                continue
        return df


class SFObjectRecordsProvider(ISFObjectRecordProvider):
    def __init__(self, client: Salesforce):
        self.client = client

    def provide_for(self, object_name: str) -> pd.DataFrame:
        try:
            sf_object = self.client.__getattr__(object_name)
            field_names = [field['name'] for field in sf_object.describe()['fields']]
            results = self.client.query_all( "SELECT " + ", ".join(field_names) + " FROM " + object_name )
            df = pd.DataFrame(results['records'])
            df.drop(columns=['attributes'], inplace=True, errors='ignore')
            return df
        except (SalesforceMalformedRequest, ConnectionError) as e:
            raise ProblemObtainingObjectRecords(e.message, object_name)


class SFObjectRecordsProviderChain(ISFObjectRecordProvider):
    def __init__(self, providers: [ISFObjectRecordProvider]):
        self.providers = providers

    def provide_for(self, object_name: str) -> pd.DataFrame:
        for provider in self.providers:
            df = provider.provide_for(object_name)

        return df


class SalesforceBackup(ICommandHandler):
    command_name: str = 'salesforce_backup_command'

    def __init__(
            self, client: Salesforce, provider: ISFObjectRecordProvider, notifier: EventNotifier
    ):
        self.client = client
        self.provider = provider
        self.notifier = notifier

    def handle(self, command: SalesForceBackupCommand) -> None:
        command_datetime = command.get_datetime()
        self.notifier.notify_for(SFBackupStartedEvent(command_datetime))
        description = self.client.describe()
        names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]

        for object_name in names:
            count = 1
            while count < command.number_of_retries + 1:
                try:
                    df = self.provider.provide_for(object_name)
                    self.notifier.notify_for(SFRecordObtainedEvent(
                        object_name, df.to_dict(), len(df), command_datetime
                    ))
                    break
                except ProblemObtainingObjectRecords as e:
                    count = count + 1
                    if count == command.number_of_retries + 1:
                        raise e
                    continue
        self.notifier.notify_for(SFBackupFinishedEvent(names, command_datetime))


class SFRecordObtainedEventSaver(IEventHandler):
    def __init__(
            self, mapper: S3FileMapper,
            file_path: IFilePathProvider,
            logger: logging.Logger,
            file_extension: str = '.parquet.gzip'
    ):
        self.mapper = mapper
        self.logger = logger
        self.file_path_provider = file_path
        self.file_extension = file_extension

    def handle(self, event: SFRecordObtainedEvent):
        object_name = event.get_object_name()
        file_path = self.file_path_provider.get_file_path_for(event)
        file_path = file_path + '/' + object_name + self.file_extension
        df = pd.DataFrame(event.get_object_data())
        self.mapper.save_as_parquet(
            df, file_path, index=None, compression='gzip'
        )
        self.logger.info(
            "%s %s: %s %d records saved in Geddes at %s" % (
                ColorOutput.BOLD, event.get_object_name(), ColorOutput.END, event.get_number_of_records(), file_path
            )
        )
        self.logger.debug("Dataframe for %s" % event.get_object_name())
        self.logger.debug(df.iloc[:5].to_json)


class SFBackupFinishedEventSaver(IEventHandler):
    def __init__(
            self, mapper: S3FileMapper, path_provider: IFilePathProvider, file_path: str, logger: logging.Logger
    ):
        self.mapper = mapper
        self.file_path_provider = path_provider
        self.file_path = file_path
        self.logger = logger

    def handle(self, event: SFBackupFinishedEvent):
        backups_df = self.mapper.read(self.file_path)
        stored_records_path = self.file_path_provider.get_file_path_for(event)
        backups_df.loc[len(backups_df)] = [event.get_event_datetime(), stored_records_path, event.get_record_names()]
        self.mapper.save_as_csv(
            backups_df, self.file_path, index=None
        )
        self.logger.info(
            "%sBackup Finished%s - Objects stored in Geddes: %d" % (
                ColorOutput.BOLD, ColorOutput.END, len(event.get_record_names())
            )
        )


class SFRecordObtainedEventLogger(IEventHandler):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle(self, event: SFRecordObtainedEvent):
        at_datetime = datetime.fromisoformat(event.get_command_datetime()).ctime()
        self.logger.debug(
             "%s %s %s backed up at %s." % (ColorOutput.BOLD, event.get_object_name(), ColorOutput.END, event.command_datetime)
        )
        self.logger.debug(
            "%s: %s." % (event.get_object_name(), event.__str__())
        )


class SFBackupStartedEventLogger(IEventHandler):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle(self, event: SFBackupStartedEvent):
        started_at_datetime = datetime.fromisoformat(event.backup_started_datetime).ctime()
        self.logger.info(
            "%s Backup Started %s at %s" % (
                ColorOutput.BOLD, ColorOutput.END, started_at_datetime
            )
        )


class SalesforceBackupFinishedLogger(IEventHandler):
    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def handle(self, event: SFBackupFinishedEvent):
        finished_at_datetime = datetime.fromisoformat(event.get_backup_finished_datetime()).ctime()
        self.logger.info(
            "%s Backup Finished %s at %s" % (
                ColorOutput.BOLD, ColorOutput.END, finished_at_datetime
            )
        )


class DefaultBackupCommandHandler:
    def create_new(
            self, application: Application, client_factory: ISalesforceFactory, loglevel: str = 'INFO'
    ) -> ICommandHandler:
        logger = get_app_logger('SalesforceBackups', loglevel)
        client = client_factory.create_new()

        notifier = EventNotifier()
        notifier.add_event_handler(
            SFRecordObtainedEvent.event_name,
            SFRecordObtainedEventSaver(
                create_default_s3mapper(application, SalesforceBackupConfiguration.bucket_name_raw),
                FilePathByDatetime(SalesforceBackupConfiguration.geddes_folder_path),
                logger
        ))
        notifier.add_event_handler(
            SFRecordObtainedEvent.event_name, SFRecordObtainedEventLogger(logger)
        )

        notifier.add_event_handler(
            SFBackupStartedEvent.event_name, SFBackupStartedEventLogger(logger)
        )

        notifier.add_event_handler(
            SFBackupFinishedEvent.event_name,
            SFBackupFinishedEventSaver(
                create_default_s3mapper(application, SalesforceBackupConfiguration.bucket_name_raw),
                FilePathByDatetime(SalesforceBackupConfiguration.geddes_folder_path),
                SalesforceBackupConfiguration.geddes_folder_path + '/' + 'full_backups',
                logger,
            ))
        notifier.add_event_handler(
            SFBackupFinishedEvent.event_name, SalesforceBackupFinishedLogger(logger)
        )

        provider = SFObjectRecordsLoggerProvider(SFObjectRecordsProvider(client), logger)

        return MetricsReporterDecorator(
            InitialExecutionDecorator(
                SalesforceBackup(
                    client, provider, notifier
                ), logger
            ), [TimingProfileReporter(), MemoryProfileReporter()], logger
        )



