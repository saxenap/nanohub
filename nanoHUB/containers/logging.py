import logging, logging.handlers, logging.config
from nanoHUB.logger import logging_conf, logger
from dependency_injector import containers, providers
from logging.handlers import SysLogHandler



class LoggingContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    # logging = providers.Resource(
    #     logging.config.dictConfig(logging_conf),
    #
    # )
    logging = providers.Resource(
        logging.basicConfig,
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.handlers.SysLogHandler(address=('logs.papertrailapp.com',19303)),
            logging.StreamHandler()
        ]
    )
    # log = logger()
    # log.addHandler(SysLogHandler(address=(
    #     config.remoteservicessettings.papertrail_hostname,
    #     config.remoteservicessettings.papertrail_port
    # )))
