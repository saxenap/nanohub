from dependency_injector import containers, providers
from nanoHUB.logger import logger
from nanoHUB.containers.logging import LoggingContainer
from nanoHUB.containers.dataaccess import DatabaseContainer
from nanoHUB.containers.googleapi import GoogleApiContainer
from nanoHUB.task.executors import JupyterExecutor, PythonFileExecutor, RFileExecutor, MetricsReporterDecorator, RetryingExecutorDecorator
from nanoHUB.task.executors import TimingProfileReporter, MemoryProfileReporter

from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI


class TasksContainer(containers.DeclarativeContainer):

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
        sf_login_params=sf_login_params,
        endpoint=config.salesforce.endpoint,
        logger=logger()
    )

    googleapi = providers.Container(
        GoogleApiContainer,
        config=config,
    )

    jupyter_executor = providers.Factory(
        JupyterExecutor,
        notebook_path=config.pipeline.executor_file_path,
        outfile_path=config.pathsettings.outfile_dir,
        logger=logger()
    )

    python_executor = providers.Factory(
        PythonFileExecutor,
        file_path=config.pipeline.executor_file_path,
        logger=logger()
    )

    r_executor = providers.Factory(
        RFileExecutor,
        file_path=config.pipeline.executor_file_path,
        logger=logger()
    )

    task_executor = providers.Selector(
        config.pipeline.executor_type,
        jupyter=jupyter_executor,
        ipynb=jupyter_executor,
        python=python_executor,
        py=python_executor,
        r=r_executor
    )

    metrics_executor = providers.Factory(
        MetricsReporterDecorator,
        executor=task_executor,
        metrics_reporters = [MemoryProfileReporter(), TimingProfileReporter()],
        logger=logger()
    )

    retrying_executor = providers.Factory(
        RetryingExecutorDecorator,
        executor=metrics_executor,
        retries_max_count=config.executorsettings.max_retries_on_failure,
        logger=logger()
    )

    get_executor = retrying_executor