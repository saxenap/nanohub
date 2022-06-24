from nanoHUB.application import Application
import typer
from typing import Optional
from typing import List
from nanoHUB.infrastructure.salesforce.backup import DefaultBackupCommandHandler, SalesForceBackupCommand
from nanoHUB.infrastructure.salesforce.client import SalesforceFromEnvironment


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
        fields: str = None,
        retries: int = 6,
        loglevel: str = typer.Option(
            "INFO",
            "--log-level",
            help="This option sets the logging level. eg. DEBUG, INFO, or CRITICAL"
        )
):
    """
    Run a Salesforce backup.
    """

    application = Application.get_instance(loglevel)

    handler = DefaultBackupCommandHandler().create_new(
        application, SalesforceFromEnvironment(domain), loglevel
    )
    command = SalesForceBackupCommand()
    if fields:
        command.specific_fields = fields.split(',')
    command.number_of_retries = retries
    handler.handle(command)


if __name__ == '__main__':
    app()

