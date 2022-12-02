# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 6/23/22
import json
import logging
from dataclasses import dataclass
from simple_salesforce import Salesforce, SalesforceMalformedRequest
from nanoHUB.application import Application
from nanoHUB.dataaccess.lake import create_default_s3mapper, S3FileMapper
import pandas as pd
from nanoHUB.logger import LoggerMixin
from nanoHUB.infrastructure.eventing import (
    EventNotifier, IEvent, IEventHandler, IFilePathProvider, FilePathByCommandDatetime
)
from nanoHUB.command import (
    ICommandHandler,
    ICommand,
    MetricsReporterDecorator,
    InitialExecutionDecorator,
    TimingProfileReporter,
    MemoryProfileReporter
)
from requests.exceptions import ConnectionError
from nanoHUB.infrastructure.salesforce.client import ISalesforceFactory
from nanoHUB.configuration import SalesforceBackupConfiguration
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

@dataclass
class SalesForceBackupCommand(ICommand):
    number_of_retries: int
    specific_fields: []

    def __repr__(self):
        return 'SalesForceBackupCommand(number_of_retries = ' + str(self.number_of_retries) + \
               'name = ' + self.command_name + \
                'specific_fields = ' + ','.join(self.specific_fields) + \
                ')'

    def __str__(self):
        return json.dumps({
            'name': self.command_name,
            'number_of_retries': self.number_of_retries,
            'specific_fields': self.specific_fields
        })


@dataclass
class SFBackupStartedEvent(IEvent):
    backup_started_datetime: str

    def __repr__(self):
        return 'SFRecordObtainedEvent(backup_started_datetime = ' + self.backup_started_datetime  + ')'

    def __str__(self):
        return json.dumps({
            'backup_started_datetime': self.backup_started_datetime,
            'event_name': self.get_event_name()
        })


@dataclass
class SFBackupFinishedEvent(IEvent):
    record_names: []
    backup_finished_datetime: str

    def __repr__(self):
        return 'SFRecordObtainedEvent(' \
               'backup_finished_datetime = ' + self.backup_finished_datetime + \
               ', record_names = ' + str(self.record_names) + \
               ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'backup_finished_datetime': self.backup_finished_datetime,
            'record_names': self.record_names
        })


@dataclass
class SFRecordObtainedEvent(IEvent):
    object_name: str
    object_data: dict
    number_of_records: int

    def __repr__(self):
        return 'SFRecordObtainedEvent(object_name = ' + self.object_name + ', object_data = ' + str(self.object_data) + ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'object_name': self.object_name,
            'object_data': self.object_data,
            'number_of_records': self.number_of_records
        })


@dataclass
class SFRecordNotObtainedEvent(IEvent):
    object_name: str

    def __repr__(self):
        return 'SFRecordObtainedEvent(object_name = ' + self.object_name + ', object_data = ' + str(self.object_data) + ')'

    def __str__(self):
        return json.dumps({
            'event_name': self.get_event_name(),
            'object_name': self.object_name
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


class SFObjectRecordsLoggerProvider(ISFObjectRecordProvider, LoggerMixin):
    def __init__(
            self,
            inner_provider: ISFObjectRecordProvider,
    ):
        self.inner_provider = inner_provider

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
            df = pd.DataFrame()
            if len(field_names) > 0:
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
        command_datetime = command.init_datetime
        self.notifier.notify_for(
            SFBackupStartedEvent(
                backup_started_datetime=datetime.now().isoformat(),
                command_name=command.command_name,
                command_datetime=command_datetime
        ))
        description = self.client.describe()
        names = [obj['name'] for obj in description['sobjects'] if obj['queryable']]
        for object_name in names:
            count = 1
            while count < command.number_of_retries + 1:
                try:
                    df = self.provider.provide_for(object_name)
                    self.notifier.notify_for(SFRecordObtainedEvent(
                        object_name=object_name,
                        object_data=df.to_dict(),
                        number_of_records=len(df),
                        command_datetime=command_datetime,
                        command_name=command.command_name
                    ))
                    break
                except ProblemObtainingObjectRecords as e:
                    count = count + 1
                    if count < command.number_of_retries + 1:
                        continue
                    self.notifier.notify_for(SFRecordNotObtainedEvent(
                        object_name=object_name,
                        command_datetime=command_datetime,
                        command_name=command.command_name
                    ))
                    # raise e
                    break
        self.notifier.notify_for(SFBackupFinishedEvent(
            record_names=names,
            backup_finished_datetime=datetime.now().isoformat(),
            command_datetime=command_datetime,
            command_name=command.command_name
        ))


class SFRecordObtainedEventSaver(IEventHandler, LoggerMixin):
    def __init__(
            self, mapper: S3FileMapper,
            file_path: IFilePathProvider,
            log_every_records: int,
            file_extension: str = '.parquet.gzip'
    ):
        self.mapper = mapper
        self.file_path_provider = file_path
        self.file_extension = file_extension
        self.log_every_records = log_every_records
        self.count = 0

    def handle(self, event: SFRecordObtainedEvent):
        object_name = event.object_name
        file_path = self.file_path_provider.file_path_for_event(event)
        file_path = file_path + '/' + object_name + self.file_extension
        df = pd.DataFrame(event.object_data)
        self.mapper.save_as_parquet(
            df, file_path, index=None, compression='gzip'
        )
        msg = "%s %s: %s %d records saved in Geddes at %s" % (
            ColorOutput.BOLD, event.object_name, ColorOutput.END, event.number_of_records, file_path
        )
        self.count = self.count + 1
        if self.log_every_records == self.count:
            self.logger.info(msg)
            self.count = 0
        else:
            self.logger.debug(msg)

        self.logger.debug("Dataframe for %s" % event.object_name)
        self.logger.debug(df.iloc[:5].to_json)


class SFBackupFinishedEventSaver(IEventHandler, LoggerMixin):
    def __init__(
            self, mapper: S3FileMapper, path_provider: IFilePathProvider, file_path: str
    ):
        self.mapper = mapper
        self.file_path_provider = path_provider
        self.file_path = file_path

    def handle(self, event: SFBackupFinishedEvent):
        if not self.mapper.exists(self.file_path):
            self.mapper.save_as_csv(pd.DataFrame(),self.file_path)

        backups_df = self.mapper.read(self.file_path)
        stored_records_path = self.file_path_provider.file_path_for_event(event)
        backups_df.loc[len(backups_df)] = [event.get_event_name(), stored_records_path, event.record_names]
        self.mapper.save_as_csv(
            backups_df, self.file_path, index=None
        )
        self.logger.info(
            "%sBackup Finished%s - Objects stored in Geddes: %d" % (
                ColorOutput.BOLD, ColorOutput.END, len(event.record_names)
            )
        )
        self.logger.info(
            "%sBackup Finished%s - Objects stored in Geddes: %d" % (
                ColorOutput.BOLD, ColorOutput.END, len(event.record_names)
            )
        )


class SFRecordObtainedEventLogger(IEventHandler, LoggerMixin):
    def __init__(self, log_every_events: int):
        self.log_every_events = log_every_events
        self.count = 0
        self.events_to_log = []

    def handle(self, event: SFRecordObtainedEvent):
        at_datetime = datetime.fromisoformat(event.command_datetime).ctime()
        self.count = self.count + 1
        msg1 = "%s %s %s backed up at %s." % (ColorOutput.BOLD, event.object_name, ColorOutput.END, event.command_datetime)
        # msg2 = "%s: %s." % (event.object_name, event.__str__())
        msg3 = "%s %s %s backed up at %s." % (ColorOutput.BOLD, ', '.join(self.events_to_log), ColorOutput.END, event.command_datetime)
        if self.count == self.log_every_events:
            self.logger.info(msg1)
            # self.logger.debug(msg2)
            self.count = 0
            self.events_to_log = []
        else:
            self.logger.debug(msg1)
            # self.logger.debug(msg2)
            self.events_to_log.append(event.object_name)


class SFRecordNotObtainedHandler(IEventHandler, LoggerMixin):
    def handle(self, event: SFRecordNotObtainedEvent):
        at_datetime = datetime.fromisoformat(event.command_datetime).ctime()
        msg1 = "%s %s %s - Records not obtained at %s." % (ColorOutput.BOLD, event.object_name, ColorOutput.END, event.command_datetime)
        self.logger.info(msg1)


class SFBackupStartedEventLogger(IEventHandler, LoggerMixin):
    def handle(self, event: SFBackupStartedEvent):
        started_at_datetime = datetime.fromisoformat(event.backup_started_datetime).ctime()
        self.logger.info(
            "%s Backup Started %s at %s" % (
                ColorOutput.BOLD, ColorOutput.END, started_at_datetime
            )
        )


class SalesforceBackupFinishedLogger(IEventHandler, LoggerMixin):
    def handle(self, event: SFBackupFinishedEvent):
        finished_at_datetime = datetime.fromisoformat(event.backup_finished_datetime).ctime()
        self.logger.info(
            "%s Backup Finished %s at %s" % (
                ColorOutput.BOLD, ColorOutput.END, finished_at_datetime
            )
        )


class DefaultBackupCommandHandler:
    def create_new(
            self, application: Application, client_factory: ISalesforceFactory
    ) -> ICommandHandler:
        s3_client = create_default_s3mapper(application, SalesforceBackupConfiguration.bucket_name_raw)

        notifier = EventNotifier()
        notifier.add_event_handler(
            SFRecordObtainedEvent.get_event_name(),
            SFRecordObtainedEventSaver(
                s3_client,
                FilePathByCommandDatetime(SalesforceBackupConfiguration.geddes_folder_path),
                5
            ))
        notifier.add_event_handler(
            SFRecordObtainedEvent.get_event_name(), SFRecordObtainedEventLogger(5)
        )

        notifier.add_event_handler(
            SFBackupStartedEvent.get_event_name(), SFBackupStartedEventLogger()
        )

        notifier.add_event_handler(
            SFBackupFinishedEvent.get_event_name(),
            SFBackupFinishedEventSaver(
                s3_client,
                FilePathByCommandDatetime(SalesforceBackupConfiguration.geddes_folder_path),
                SalesforceBackupConfiguration.full_backups_geddes_file_path
            ))
        notifier.add_event_handler(
            SFBackupFinishedEvent.get_event_name(), SalesforceBackupFinishedLogger()
        )

        notifier.add_event_handler(
            SFRecordNotObtainedEvent.get_event_name(), SFRecordNotObtainedHandler()
        )

        client = client_factory.create_new()

        provider = SFObjectRecordsLoggerProvider(
                SFObjectRecordsProvider(client)
        )

        return MetricsReporterDecorator(
            InitialExecutionDecorator(
                SalesforceBackup(
                    client, provider, notifier
                )
            ), [TimingProfileReporter(), MemoryProfileReporter()]
        )