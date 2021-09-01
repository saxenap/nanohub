from nanoHUB.application import Application
from nanoHUB.logger import logger
import typer
from typing import List

app = typer.Typer()
task_app = typer.Typer(help="Manage tasks.")
app.add_typer(task_app, name="task")


@task_app.command()
def execute(
        file_paths: List[str],
        loglevel: str = typer.Option(
            "INFO",
            "--log-level",
            help="This option sets the logging level. eg. DEBUG, INFO, or CRITICAL", prompt="Enter logging level or press enter to set default:"
        )
):
    """
    Execute task(s) defined in .py or .ipynb files.
    """

    if not file_paths:
        typer.echo("File path for file to be executed not provided.")
        raise typer.Abort()

    application = Application.get_instance()
    application.execute(file_paths)
    logger(__name__).info("Task called")


if __name__ == '__main__':
    app()

