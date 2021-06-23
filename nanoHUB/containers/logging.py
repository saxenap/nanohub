import logging, logging.config
from nanoHUB.logger import logging_conf
from dependency_injector import containers, providers



class LoggingContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    logging = providers.Resource(
        logging.config.dictConfig(logging_conf)
    )