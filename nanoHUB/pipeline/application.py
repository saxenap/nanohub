from dependency_injector import containers, providers
from nanoHUB.settings import Settings
from nanoHUB.logger import logger
from nanoHUB.core_containers import LoggingContainer, DatabaseContainer
from nanoHUB.pipeline.executors import JupyterExecutor, PythonFileExecutor, LoggingExecutorDecorator, RetryingExecutorDecorator
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import os, sys


class Application(containers.DeclarativeContainer):

    config = providers.Configuration()

    logging = providers.Container(
        LoggingContainer,
        config=config,
    )

    database = providers.Container(
        DatabaseContainer,
        config=config,
    )

    sf_login_params = providers.Dict({
        'grant_type': config.salesforce.grant_type,
        'client_id': config.salesforce.client_id,
        'client_secret': config.salesforce.client_secret,
        'username': config.salesforce.username,
        'password': config.salesforce.password,
    })

    salesforce = providers.Factory(
        DB2SalesforceAPI,
        sf_login_params=sf_login_params
    )

    jupyter_executor = providers.Factory(
        JupyterExecutor,
        notebook_path=config.pipeline.executor_file_path,
        outfile_path=config.pathsettings.outfile_dir,
        logger=logger(__name__)
    )

    python_executor = providers.Factory(
        PythonFileExecutor,
        file_path=config.pipeline.executor_file_path,
        logger=logger(__name__)
    )

    task_executor = providers.Selector(
        config.pipeline.executor_type,
        jupyter=jupyter_executor,
        ipynb=jupyter_executor,
        python=python_executor,
        py=python_executor,
    )

    logging_executor = providers.Factory(
        LoggingExecutorDecorator,
        executor=task_executor,
        file_path=config.pipeline.executor_file_path,
        logger=logger(__name__)
    )

    retrying_executor = providers.Factory(
        RetryingExecutorDecorator,
        executor=logging_executor,
        retries_max_count=config.executorsettings.max_retries_on_failure,
        logger=logger(__name__)
    )

    get_executor = retrying_executor

    self_instance: 'Application' = None


    def set_filepath(filepath: str):
        self = Application.get_instance()
        self.config.set('pipeline.executor_file_path', filepath)
        self.config.set('pipeline.executor_type', os.path.splitext(filepath)[1].lstrip('.'))


    @staticmethod
    def get_instance():
        if Application.self_instance is None:
            self = Application()
            self.config.from_pydantic(Settings())
            self.wire(modules=[sys.modules[__name__]])
            Application.self_instance = self

        return Application.self_instance


class Facade:
    application: Application = Application()



