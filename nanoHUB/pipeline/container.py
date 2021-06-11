from dependency_injector import containers, providers
from nanoHUB.logger import logger
from nanoHUB.core_containers import LoggingContainer, DatabaseContainer
from nanoHUB.pipeline.executors import JupyterExecutor, PythonFileExecutor, LoggingExecutorDecorator, RetryingExecutorDecorator, TimeProfilingDecorator, MemoryProfilingDecorator
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI
import datetime


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

    time_profiling_executor = providers.Factory(
        TimeProfilingDecorator,
        executor=logging_executor,
        logger=logger(__name__)
    )

    memory_profiling_executor = providers.Factory(
        MemoryProfilingDecorator,
        executor=time_profiling_executor,
        logger=logger(__name__)
    )

    get_executor = memory_profiling_executor