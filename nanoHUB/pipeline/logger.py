
import logging, logging.config


def logger():
    return logging.getLogger(__name__)


conf = dict(
    version = 1,
    disable_existing_loggers = False,
    formatters = dict(
        simple = dict(
            format = "%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s"
        )
    ),
    handlers = dict(
        console = dict(
            **{'class': 'logging.StreamHandler'},
            level = logging.DEBUG,
            formatter = 'simple',
            stream = 'ext://sys.stdout'
        ),
        info_file_handler = dict(
            **{'class': 'logging.handlers.RotatingFileHandler'},
            level = logging.INFO,
            formatter = 'simple',
            filename = '.log/info.log',
            maxBytes = 10485760,
            backupCount = 20,
            encoding = 'utf8'
        ),
        error_file_handler = dict(
            **{'class': 'logging.handlers.RotatingFileHandler'},
            level = logging.ERROR,
            formatter = 'simple',
            filename = '.log/errors.log',
            maxBytes = 10485760,
            backupCount = 20,
            encoding = 'utf8'
        )
    ),
    loggers = dict(
        nanoHUB = dict(
            level = logging.NOTSET,
            handlers = ['console', 'info_file_handler', 'error_file_handler'],
            propagate = False
        )
    ),
    root = dict(
        level = logging.NOTSET,
        handlers = ['console', 'info_file_handler', 'error_file_handler']
    )
)

logging.config.dictConfig(conf)
