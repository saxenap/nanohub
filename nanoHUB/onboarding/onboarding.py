import os
import subprocess
from IPython.display import display, HTML, Javascript
from ipywidgets import *
from dataclasses import dataclass
import json
import logging
import re


#widget functionality for ipynb input
@dataclass
class InputWidgetValueMap:
    fullname: str
    email: str
    username: str
    password: str
    passwordv: str


@dataclass
class SSHParams:
    email: str
    key: str


def _input(placeholder: str, description: str, is_disabled: bool = False):
    inwid = widgets.Text(
        placeholder=placeholder,
        description=description,
        disabled=is_disabled
    )
    display(inwid)
    return inwid

def _password(placeholder: str, description: str, is_disabled: bool = False):
    p = widgets.Password(
        placeholder=placeholder,
        description=description,
        disabled=is_disabled
    )
    display(p)
    return p

def _fullname():
    value = _input("Enter your full name", 'Full name:')
    # print(value)
    return value

def _email():
    value = _input('Enter your email address', 'Email:')
    # print(value)
    return value

def _username():
    value = _input('Enter your username', 'Username:')
    # print(value)
    return value

def _password_first():
    value = _password('Enter new password', 'Password')
    # print(value)
    return value

def _password_reenter():
    value = _password('Re-enter new password', 'Re-enter')
    return value

def _newline():
    display(HTML("</Br>"))


class UserInputError(RuntimeError):
    """placeholdertext"""


class Setup:

    def init(self):
        self.form = FormSetup()
        return self

    def create_form(self):
        self.inputs = self.form.execute()  # sets the passwords again after form is completed


class FormSetup:
    def execute(self):
        display(HTML(
            "</Br>DO NOT RUN THE ENTIRE FILE AT ONCE. ONCE YOU FILL IN THE FORM, RUN THE generate_ssh() CELL."
        ))
        _newline()
        email = _email()
        fullname = _fullname()
        username = _username()
        display(HTML(
            "</Br>Your current password to access this server is \"nanoHUB\". You should change this password. Please enter the new password. </Br>You must change it for security reasons."
        ))
        _newline()
        password1 = _password_first()
        password2 = _password_reenter()
        _newline()

        return InputWidgetValueMap(fullname, email, username, password1, password2)

#END OF WIDGET FUNCTIONALITY

#Start of CORE FUNCTIONALITY
@dataclass
class OnboardingCommand:
    git_fullname: str
    git_email: str
    git_username: str
    # jupyter_password: str
    env_career_user: str
    env_career_password: str
    env_ssh_db_user: str
    env_ssh_db_pass: str
    geddes_user: str
    geddes_secret_key: str
    geddes_access_key: str
    repo_ssh_url: str = 'git@gitlab.hubzero.org:saxenap/nanohub-analytics.git'
    local_dir_path: str = '/home/saxenap'
    dir_name_for_repository: str = 'nanoHUB'

#Setup Actions

    #git

def _kill_agent():
    logging.debug('killing previously started ssh-agent')
    subprocess.run(['ssh-agent', '-k'])
    del os.environ['SSH_AUTH_SOCK']
    del os.environ['SSH_AGENT_PID']


_OUTPUT_PATTERN = re.compile(r'SSH_AUTH_SOCK=(?P<SSH_AUTH_SOCK>[^;]+).*SSH_AGENT_PID=(?P<SSH_AGENT_PID>\d+)', re.MULTILINE | re.DOTALL)
def parse_ssh_agent(output):
    match = _OUTPUT_PATTERN.search(output)
    if match is None:
        raise Exception(f'Could not parse ssh-agent output. It was: {output}')
    return match.groupdict()


def _setup_agent():
    process = subprocess.run(['ssh-agent', '-s'], stdout=subprocess.PIPE, text=True)
    agent_data = parse_ssh_agent(process.stdout)
    logging.debug('ssh agent data: {}'.format(agent_data))
    logging.debug('exporting ssh agent environment variables')
    os.environ['SSH_AUTH_SOCK'] = agent_data['SSH_AUTH_SOCK']
    os.environ['SSH_AGENT_PID'] = agent_data['SSH_AGENT_PID']


class SSH_Setup:
    def generate_for(self, email_address: str, root_folder: str) -> str:
        pub_file_path = "%s/.ssh/id_rsa.pub" % (root_folder)
        cmd1 = os.system("rm -rf %s/.ssh/id* %s/.ssh/.id*" % (root_folder, root_folder))
        cmd2 = os.system("yes '' | ssh-keygen -N '' -C '%s' > /dev/null" % (email_address))
        cmd3 = os.system('cat %s' % (pub_file_path))
        sshkey = os.popen('cat %s' % (pub_file_path)).read()
        # cmd01 = os.system('eval "$(ssh-agent -s >/dev/null)"')
        _setup_agent()
        # cmd02 = os.system('ssh-add ~/.ssh/id_rsa')

        process = subprocess.run(['ssh-add', pub_file_path])
        if process.returncode != 0:
            raise Exception('failed to add the key: {}'.format(pub_file_path))
        cmd03 = os.system('ssh-keyscan -t rsa gitlab.hubzero.org >> ~/.ssh/known_hosts')
        return sshkey


class GitUserConfiguration:
    def configure_for(self, username, fullname, email):
        cmd2_1 = os.system("git config --global user.name '%s'" % fullname)
        cmd2_2 = os.system("git config --global user.email '%s'" % email)
        cmd2_2 = os.system("git config --global credential.username '%s'" % username)


class GitRepositoryConfiguration:
    def configure_for(self, repo_ssh_url: str, local_dir_path: str):
        cmd1 = os.system("cd %s" % local_dir_path)
        cmd2 = os.system("git clone git@gitlab.hubzero.org:saxenap/nanohub-analytics.git temp")


    #env
class ENV_Setup:
    def configure_env(self, command: OnboardingCommand):
        self.create_env(command)
        env = open(command.local_dir_path + '/' + command.dir_name_for_repository + '/temp/nanoHUB/.env', "r") #read .env
        data = env.read()
        env.close()

        #if error: requires modified .dev.env file, with {} around the keys in the below call

        data = data.format(CAREER_ACCOUNT_USERNAME_HERE = command.env_career_user,
                CAREER_ACCOUNT_PASSWORD_HERE = command.env_career_password,
                DB_USERNAME_HERE = command.env_ssh_db_user,
                DB_PASSWORD_HERE = command.env_ssh_db_pass,
                GEDDES_USERNAME_HERE = command.geddes_user,
                GEDDES_SECRET_KEY_HERE = command.geddes_secret_key,
                GEDDES_ACCESS_KEY_HERE = command.geddes_access_key)

        envout = open(command.local_dir_path + '/' + command.dir_name_for_repository + '/temp/nanoHUB/.env', 'w') #write .env
        envout.write(data)
        envout.close()
        self.export_env(command)

    def create_env(self, command: OnboardingCommand):
        cmd1 = os.system("cp " + command.local_dir_path + '/' + command.dir_name_for_repository + '/temp/nanoHUB/' + '.env.dev' +
                         " " +
                         command.local_dir_path + '/' + command.dir_name_for_repository + '/temp/nanoHUB/' + ".env")

    def export_env(self, command: OnboardingCommand):
        cmd1 = os.system('set -o allexport')
        cmd2 = os.system('. ' + command.local_dir_path + '/' + command.dir_name_for_repository + '/temp/nanoHUB/' + ".env")
        cmd3 = os.system('set +o allexport')


#CommandMapper
class IOnboardingCommandMapper:
    def create_new(self) -> OnboardingCommand:
        raise NotImplementedError

class JupyterCommandMapper(IOnboardingCommandMapper):
    def __init__(self, form):
        self.form = form

    def create_new(self) -> OnboardingCommand:
        inputs = self.form.execute()
        if inputs.password.value == inputs.passwordv.value:
            return OnboardingCommand(
                inputs.fullname.value,
                inputs.email.value,
                inputs.username.value,
                inputs.password.value
            )
        else:
            raise UserInputError("Make sure your passwords match")

#Validator/Error Indicator
class CommandErrors:
    def __init__(self):
        self.errors_by_key = {}

    def set_error_for(self, key: str, error: str) -> None:
        self.errors_by_key[key] = error

    def get_errors(self) -> {}:
        return self.errors_by_key

    def has_errors(self) -> bool:
        return bool(self.errors_by_key)


class CommandValidator:
    def __init__(self, errors: CommandErrors):
        self.errors = errors

    def git_validate(self, command: OnboardingCommand) -> CommandErrors:
        # git
        # fullname
        if command.git_fullname == "":
            self.errors.set_error_for('name', 'Full name field is empty!')

        # email
        if command.git_email == "":
            self.errors.set_error_for('email', 'Email field is empty!')

        # username
        if command.git_username == "":
            self.errors.set_error_for('name', 'Username field is empty!')

        # jupyterpassword
        # if command.jupyter_password == "":
        #     self.errors.set_error_for('password', 'Jupyter password field is empty!')

        return self.errors

    def env_validate(self, command: OnboardingCommand) -> CommandErrors:
        # env
        # career username
        if command.env_career_user == "":
            self.errors.set_error_for('career account username', 'Career account username field is empty!')

        # career password
        if command.env_career_password == "":
            self.errors.set_error_for('career account password', 'Career account password field is empty!')

        # db username
        if command.env_ssh_db_user == "":
            self.errors.set_error_for('db username', 'Database username field is empty!')

        # db password
        if command.env_ssh_db_pass == "":
            self.errors.set_error_for('db password', 'Database password field is empty!')

        return self.errors


#Command
class ICommand:
    def __str__(self) -> str:
        raise NotImplementedError


class EnvSetupCommand(ICommand):
    # def __init__(self, ):
    def __str__(self) -> str:
        return str(OnboardingCommand)


class GitSetupCommand(ICommand):
    def __str__(self) -> str:
        return str(OnboardingCommand)


#Processor
class ICommandProcessor:
    def process(self, command: ICommand) -> None:
        raise NotImplementedError

    def can_handle(self, command: ICommand) -> bool:
        raise NotImplementedError


class GitProcessor(ICommandProcessor): #OnboardingProcessor
    def __init__(
            self,
            validator: CommandValidator,
            ssh: SSH_Setup,
            git_user: GitUserConfiguration
    ):
        self.validator = validator
        self.ssh = ssh
        self.git_user = git_user

    def process(self, command: OnboardingCommand) -> str:
        errors = self.validator.git_validate(command)
        if errors.has_errors():
            raise UserInputError(json.dumps(errors.get_errors()))

        self.git_user.configure_for(
            command.git_username,
            command.git_fullname,
            command.git_email
        )
        sshkey = self.ssh.generate_for(command.git_email, command.local_dir_path)
        return sshkey


class GitRepositoryProcessor(ICommandProcessor): #OnboardingProcessor
    def __init__(
            self,
            validator: CommandValidator,
            git_repo: GitRepositoryConfiguration
    ):
        self.validator = validator
        self.git_repo = git_repo

    def process(self, command: OnboardingCommand):
        self.git_repo.configure_for(
            command.repo_ssh_url,
            command.local_dir_path + '/' + command.dir_name_for_repository
        )


class EnvProcessor(ICommandProcessor):
    def __init__(
            self,
            validator: CommandValidator,
            env: ENV_Setup
    ):
        self.env = env
        self.validator = validator

    def process(self, command: OnboardingCommand) -> None:
        errors = self.validator.env_validate(command)
        if errors.has_errors():
            raise UserInputError(json.dumps(errors.get_errors()))

        self.env.configure_env(command)

#Misc
# class CommandQueue:
#     def add_processor(self, ):

#Factory
class DefaultProcessorFactory:
    def create_new_for_env_credentials(self):
        return EnvProcessor(
                CommandValidator(CommandErrors()),
                ENV_Setup()
            )

    def create_new_for_git_credentials(self):
        return GitProcessor(
                CommandValidator(CommandErrors()),
                SSH_Setup(),
                GitUserConfiguration()
            )

    def create_new_for_git_repository(self):
        return GitRepositoryProcessor(
                    CommandValidator(CommandErrors()),
                    GitRepositoryConfiguration()
        )