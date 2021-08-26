import logging, logging.config


logging_conf = dict(
    version = 1,
    disable_existing_loggers = False,
    formatters = dict(
        simple = dict(
            format = "%(asctime)s - [%(levelname)s] %(name)s [%(module)s.%(funcName)s:%(lineno)d]: %(message)s",
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

    return logger
