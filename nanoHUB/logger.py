import logging, logging.config

class ModuleNameFilter(logging.Filter):

    def __init__(self, module_name: str, color: str = '\033[1m'):

        logging.Filter.__init__(self)
        self.module_name = module_name
        self.color = color

    def filter(self, record):

        if self.module_name == record.name.split('.')[0]:

            color = self.color
            stop_color = '\033[0m'
            record.name = color + record.name + stop_color
            record.pathname = color + record.pathname + stop_color
            record.levelname = color + record.levelname + stop_color
        return True


class CustomFormatter(logging.Formatter):
    """Logging Formatter to add colors and count warning / errors"""

    grey = "\x1b[38;21m"
    yellow = "\x1b[33;21m"
    red = "\x1b[31;21m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    format = "%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"

    FORMATS = {
        logging.DEBUG: red + format + reset,
        logging.INFO: red + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logging_conf = dict(
    version = 1,
    disable_existing_loggers = False,
    formatters = dict(
        simple = dict(
            format = "%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
        ),
        colored = dict(
            **{'class': 'nanoHUB.logger.CustomFormatter'}
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
            formatter = 'simple',
            address = '/dev/log'
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
            level = logging.WARNING,
            handlers = [
                'console',
                'syslog'
            ],
            propagate = True
        ),
        sshtunnel = dict(
            level = logging.CRITICAL,
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


def logger(name: str = None):
    if name == None :
        logger =  logging.getLogger()
    else:
        logger = logging.getLogger().getChild(name)

    # print(logger.handlers)
    # handler = logger.handlers[0]
    # handler.setFormatter(CustomFormatter())
    logger.addFilter(ModuleNameFilter('nanoHUB'))
    return logger


