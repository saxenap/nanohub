import logging

from nanoHUB.application import Application
import typer
from typing import Optional
from typing import List
from nanoHUB.infrastructure.salesforce.backup import DefaultBackupCommandHandler, SalesForceBackupCommand, SFBackupStartedEvent
from nanoHUB.infrastructure.salesforce.client import SalesforceFromEnvironment
import logging.config
from nanoHUB.logger import logging_conf


app = typer.Typer()
task_app = typer.Typer(help="Manage Tasks.")
app.add_typer(task_app, name="task")
backup_app = typer.Typer(help="Run Salesforce Backups.")
app.add_typer(backup_app, name="backup")

@task_app.command()
def execute(
        file_paths: List[str],
        loglevel: str = typer.Option(
            "INFO",
            "--log-level",
            help="This option sets the logging level. eg. DEBUG, INFO, or CRITICAL"
        )
):
    """
    Execute task(s) defined in .py or .ipynb files.
    """
    if not file_paths:
        typer.echo("File path for file to be executed not provided.")
        raise typer.Abort()

    application = Application.get_instance(loglevel)
    application.execute(file_paths)


@backup_app.command()
def salesforce(
        domain: str,
        # retries: int,
        fields: str = '',
        loglevel: str = typer.Option(
            "INFO",
            "--log-level",
            help="This option sets the logging level. eg. DEBUG, INFO, or CRITICAL"
        )
):
    """
    Run a Salesforce backup.
    """
    logging.config.dictConfig(logging_conf)
    logging.getLogger().setLevel(logging.getLevelName(loglevel.upper()))

    application = Application.get_instance(loglevel)

    handler = DefaultBackupCommandHandler().create_new(
        application, SalesforceFromEnvironment(domain)
    )
    command = SalesForceBackupCommand(
        number_of_retries=6,
        specific_fields=fields.split(','),
        log_level=loglevel,
    )
    handler.handle(command)


if __name__ == '__main__':
    app()

