import logging

from nanoHUB.application import Application
import typer
from typing import Optional
from typing import List
from nanoHUB.infrastructure.salesforce.backup import DefaultBackupCommandHandler, SalesForceBackupCommand, SFBackupStartedEvent
from nanoHUB.infrastructure.salesforce.client import SalesforceFromEnvironment
import logging.config
from nanoHUB.logger import logging_conf
from nanoHUB.onboarding.onboarding import OnboardingCommand, DefaultProcessorFactory

app = typer.Typer()
task_app = typer.Typer(help="Manage Tasks.")
app.add_typer(task_app, name="task")
backup_app = typer.Typer(help="Run Salesforce Backups.")
app.add_typer(backup_app, name="backup")
onboard_app = typer.Typer(help="Onboarding for Data Work.")
app.add_typer(onboard_app, name="onboard")

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
    logging.config.dictConfig(logging_conf)
    logging.getLogger().setLevel(logging.getLevelName(loglevel.upper()))

    application = Application.get_instance(loglevel)
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


@onboard_app.command()
def user(
        purdue_career_username: str = typer.Argument(default='', help="This is your Purdue career account username."),
        purdue_career_password: str = typer.Argument(default='', help="This is your Purdue career account password."),
        database_username: str = typer.Argument(default='', help="This is the database username given to you to access the nanoHUB database. This username is typically suffixed by _ro"),
        database_password: str = typer.Argument(default='', help="This is the database password given to you to access the nanoHUB database. This password is typically found in the .my.cnf file in your root directory on the server."),
        gitlab_email: str = typer.Argument(default='', help="This is the email address you'd like to use for GitLab. Typically, this email address is your Purdue email."),
        gitlab_username: str = typer.Argument(default='', help="This is the username you'd like to use for GitLab"),
        gitlab_fullname: str = typer.Argument(default='', help="This is your full name. Eg. Casey Willinamo.")
):
    """
    Onboard a user.
    """
    command = OnboardingCommand(
        git_fullname= gitlab_fullname,
        git_email= gitlab_email,
        git_username= gitlab_username,
        jupyter_password= 'nanoHUB',
        env_career_user= purdue_career_username,
        env_career_password= purdue_career_password,
        env_ssh_db_user= database_username,
        env_ssh_db_pass= database_password
    )

    factory = DefaultProcessorFactory()

    git_processor = factory.create_new_for_git_credentials()
    ssh_key = git_processor.process(command)

    print(ssh_key)
    input("Press any key to continue...")

    git_repo_processor = factory.create_new_for_git_repository()
    git_repo_processor.process(command)

    env_processor = factory.create_new_for_env_credentials()
    env_processor.process(command)


if __name__ == '__main__':
    app()

