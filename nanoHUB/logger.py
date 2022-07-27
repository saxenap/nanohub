import logging, logging.config
from sshtunnel import SSHTunnelForwarder


logging_conf = dict(
    version = 1,
    disable_existing_loggers = False,
    formatters = dict(
        simple = dict(
            format = "[%(levelname)s] [%(module)s - %(name)s]: %(message)s [%(module)s.%(funcName)s:%(lineno)d]",
        ),
        remote = dict(
            format = "%(message)s [%(module)s - %(name)s]: [%(module)s.%(funcName)s:%(lineno)d]",
        )
    ),
    handlers = dict(
        console = dict(
            **{'class': 'logging.StreamHandler'},
            level = logging.INFO,
            formatter = 'simple',
            stream = 'ext://sys.stdout'
        ),
        syslog = dict(
            **{'class': 'logging.handlers.SysLogHandler'},
            level = logging.INFO,
            formatter = 'remote',
            address = ('logs.papertrailapp.com', 19303)
        )
    ),
    loggers = dict(
        root = dict(
            level = logging.NOTSET,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = True
        ),
        paramiko = dict(
            level = logging.ERROR,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = True
        ),
        sshtunnel = dict(
            level = logging.ERROR,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = False
        ),
        SSHTunnelForwarder = dict(
            level = logging.ERROR,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = False
        ),
        papermill = dict(
            level = logging.ERROR,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = False
        )
    ),
    root = dict(
        level = logging.NOTSET,
        handlers = [
            'console',
            'syslog'
        ]
    )
)


def logger(name: str = '', loglevel: str = 'INFO') -> logging.Logger:
    loglevel = loglevel.upper()
    level = logging.getLevelName(loglevel)

    # if name == None :
    #     logger =  logging.getLogger()
    # else:
    logger = logging.getLogger(name)

    logger.setLevel(level)

    return logger


def get_logger_with_level(name: str = None, loglevel: str = 'INFO') -> logging.Logger:
    return logger(name, loglevel)


class LoggerMixin():
    @property
    def logger(self):
        component = "{}.{}".format(type(self).__module__, type(self).__name__)
        return logging.getLogger(component)
