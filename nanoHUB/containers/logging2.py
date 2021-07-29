from dependency_injector import containers, providers
import sys
import logging
import random
import string
from logging import LoggerAdapter, getLogger, StreamHandler
from logging.handlers import RotatingFileHandler, SysLogHandler


class UniqueIdAdapter(LoggerAdapter):

    def __init__(self, logger, unique_id: str = None):
        super(LoggerAdapter, self).__init__(logger, {})
        self.unique_id = unique_id

    def process(self, msg, kwargs):
        if not self.unique_id:
            alphabet = string.ascii_lowercase + string.digits
            self.unique_id = ''.join(random.choices(alphabet, k=8))

        return '[%s] %s' % (self.unique_id, msg), kwargs


class AbstractLoggerFactory:

    def __init__(self, config, allow_others: bool = False):
        self.config = config
        self.allow_others = allow_others
        self.logger = logging.getLogger(config.app.name)

    def create(self) -> logging.Logger:
        raise NotImplementedError


class JupyterLoggerFactory(AbstractLoggerFactory):

    def create(self) -> logging.Logger:

        config = self.config
        logger = self.logger

        file_handler = RotatingFileHandler(
            config.jupyter.logging_file_dir + '/' + config.jupyter.logging_file_name,
            maxBytes=config.jupyter.logging_file_max_bytes,
            backupCount=config.jupyter.logging_file_backup_count
        )

        file_handler.setLevel(
            logging.getLevelName(config.jupyter.logging_file_level)
        )

        file_handler.setFormatter(
            logging.Formatter(config.jupyter.logging_file_msg_format)
        )

        logger.addHandler(file_handler)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(
            logging.getLevelName(config.jupyter.logging_stdout_level)
        )
        stream_handler.setFormatter(
            logging.Formatter(config.jupyter.logging_stdout_msg_format)
        )
        logger.addHandler(stream_handler)
        return logger


class PipelineLoggerFactory(AbstractLoggerFactory):

    def create(self) -> logging.Logger:

        config = self.config
        logger = self.logger

        stream_handler = StreamHandler(sys.stdout)
        stream_handler.setLevel(
            logging.getLevelName(config.pipeline.logging_stdout_level)
        )
        stream_handler.setFormatter(
            logging.Formatter(config.pipeline.logging_stdout_msg_format)
        )
        logger.addHandler(stream_handler)

        syslog_handler = SysLogHandler()
        syslog_handler.setLevel(
            logging.getLevelName(config.pipeline.logging_syslog_level)
        )
        syslog_handler.setFormatter(
            logging.Formatter(config.pipeline.logging_syslog_msg_format)
        )
        logger.addHandler(syslog_handler)

        return logger


class PapertrailLoggingDecorator:

    def __init__(self, logger_factory: AbstractLoggerFactory, config):
        self.config = config
        self.logger_factory = logger_factory


    def get_logger(self) -> logging.Logger:
        config = self.config
        syslog_handler = SysLogHandler(address = (config.papertrail.url, config.papertrail.port))
        syslog_handler.setLevel(
            logging.getLevelName(config.pipeline.logging_syslog_level)
        )
        syslog_handler.setFormatter(
            logging.Formatter(config.pipeline.logging_syslog_msg_format)
        )

        logger = self.logger_factory.create()
        logger.addHandler(syslog_handler)

        return logger


class LoggingContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    JupyterLoggerFactory = providers.Factory(
        JupyterLoggerFactory,
        config=config
    )

    PipelineLoggerFactory = providers.Factory(
        PipelineLoggerFactory,
        config=config
    )

    logging_selector = providers.Selector(
        config.logging.type,
        jupyter=JupyterLoggerFactory,
        pipeline=PipelineLoggerFactory
    )

    papertrail_logging = providers.Factory(
        PapertrailLoggingDecorator,
        logger_factory=logging_selector,
        config=config
    )

    logging = papertrail_logging
