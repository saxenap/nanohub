from nanoHUB.containers.tasks import TasksContainer
from nanoHUB.settings import Settings
from nanoHUB.dataaccess.connection import IDbConnectionFactory
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import os, sys, logging
from nanoHUB.logger import logger as log

class Application:

    def __init__(self, container: TasksContainer):
        self.container = container
        if os.environ.get('APP_DIR') is not None:
            dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
            os.environ['APP_DIR'] = dir_path
            os.environ['APP_DIR_TEST'] = dir_path

    def new_db_engine(self, db_name: str) -> IDbConnectionFactory:

        return self.container.database.db_connection_factory().get_connection_for(db_name)

    def new_salesforce_engine(self) -> DB2SalesforceAPI:

        return self.container.salesforce()

    def new_google_api_engine(self):

        return self.container.googleapi.googleapi_service().create_new_service(os.environ["APP_DIR"])

    def get_configuration(self):
        return self.container.config

    def get_config_value(self, key_name: str):
        return self.get_configuration().get(key_name)

    def execute(self, file_paths: [str]):
        for file_path in file_paths:
            self.container.config.set('pipeline.executor_file_path', file_path)
            self.container.config.set('pipeline.executor_type', os.path.splitext(file_path)[1].lstrip('.'))
            executor = self.container.get_executor()
            executor()

    default_instance: 'Application' = None

    @staticmethod
    def get_instance(loglevel: str = 'INFO') -> 'Application':

        if Application.default_instance is None:
            container = TasksContainer()
            container.config.from_pydantic(Settings())
            container.wire(modules=[sys.modules[__name__]])
            loglevel = loglevel.upper()
            level = logging.getLevelName(loglevel)

            if loglevel == 'DEBUG':
                loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
                for logger in loggers:
                    logger.setLevel(logging.DEBUG)

            logger = log()
            logger.setLevel(level)
            Application.default_instance = Application(container)

        return Application.default_instance
