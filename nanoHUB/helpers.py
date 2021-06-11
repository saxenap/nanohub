from nanoHUB.core_containers import DatabaseContainer
from nanoHUB.settings import Settings
from nanoHUB.connection import IDbConnectionFactory
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
from nanoHUB.pipeline.application import Application
import sys


class ConnectionFactory:

    def new_for_db(self, db_name: str) -> IDbConnectionFactory:

        container = DatabaseContainer()
        container.config.from_pydantic(Settings())
        container.wire(modules=[sys.modules[__name__]])
        return container.db_connection_factory().get_connection_for(db_name)

    def new_for_salesforce(self) -> DB2SalesforceAPI:

        container = Application.get_instance()
        container.config.from_pydantic(Settings())
        container.wire(modules=[sys.modules[__name__]])
        return container.salesforce()