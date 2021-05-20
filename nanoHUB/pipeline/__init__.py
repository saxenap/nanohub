import logging, logging.config
from nanoHUB.config.logger import conf as logger_configuration
logging.config.dictConfig(logger_configuration)


def logger():
    return logging.getLogger(__name__)
