from dependency_injector import containers, providers
from nanoHUB.dataaccess.connection import DbConnectionParams, PyMysqlConnectionFactory, TunneledConnectionParams, TunneledConnectionFactory
from nanoHUB.logger import logger
import logging



class DatabaseContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    db_params = providers.Factory(
        DbConnectionParams,
        db_host = config.database.host,
        db_username = config.database.user,
        db_password = config.database.password,
        db_port = config.database.port
    )

    db_connection_factory_inner = providers.Factory(
        PyMysqlConnectionFactory,
        db_params
    )

    tunneled_connection_params = providers.Factory(
        TunneledConnectionParams,
        ssh_host = config.sshtunnel.host,
        ssh_username = config.sshtunnel.username,
        ssh_password = config.sshtunnel.password,
        ssh_port = config.sshtunnel.port,
        remote_bind_address = config.sshtunnel.remote_bind_address,
        remote_bind_port = config.sshtunnel.remote_bind_port
    )

    tunneled_connection_factory = providers.Factory(
        TunneledConnectionFactory,
        db_connection_factory_inner,
        tunneled_connection_params,
        logger=logger(__name__)
    )

    db_connection_factory = providers.Selector(
        config.sshtunnel.use_ssh_connection,
        true=tunneled_connection_factory,
        false=db_connection_factory_inner,
    )

