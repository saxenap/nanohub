from nanoHUB.containers.tasks import TasksContainer
from nanoHUB.settings import Settings
from nanoHUB.dataaccess.connection import IDbConnectionFactory
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import os, sys


class Application:

    def __init__(self, container: TasksContainer):
        self.container = container

    def new_db_engine(self, db_name: str) -> IDbConnectionFactory:

        return self.container.database.db_connection_factory().get_connection_for(db_name)

    def new_salesforce_engine(self) -> DB2SalesforceAPI:

        return self.container.salesforce()

    def execute(self, file_path: str):

        self.container.config.set('pipeline.executor_file_path', file_path)
        self.container.config.set('pipeline.executor_type', os.path.splitext(file_path)[1].lstrip('.'))
        executor = self.container.get_executor()
        executor()

    default_instance: 'Application' = None

    @staticmethod
    def get_instance() -> 'Application':

        if Application.default_instance is None:
            container = TasksContainer()
            container.config.from_pydantic(Settings())
            container.wire(modules=[sys.modules[__name__]])
            Application.default_instance = Application(container)

        return Application.default_instance
