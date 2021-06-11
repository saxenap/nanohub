import logging, logging.config


logging_conf = dict(
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
        )
    ),
    loggers = dict(
        nanoHUB = dict(
            level = logging.NOTSET,
            handlers = ['console'],
            propagate = False
        )
    ),
    root = dict(
        level = logging.NOTSET,
        handlers = ['console']
    )
)


def logger(name: str = None):
    if name == None :
        return logging.getLogger()
    return logging.getLogger().getChild(name)