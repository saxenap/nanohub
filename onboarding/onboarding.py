import os
import subprocess
from IPython.display import display, HTML, Javascript
from ipywidgets import *
from dataclasses import dataclass
import json
import re


@dataclass
class InputValueMap:
    fullname: str 
    email: str
    username: str 
    password: str
    passwordv: str
    
@dataclass
class SSHParams:
    email: str
    key: str
    # js: str
    
    
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
        self.ssh = SSH_Setup()
        self.git = GitSetup()
        self.validate = InputValidation(InputNameMap())
        return self
    
    def create_form(self):
        self.inputs = self.form.execute() #sets the passwords again after form is completed
        
    # def get_inputs(self):
    #     #for testing
    #     showvalues = []
    #     showvalues.append(self.inputs.fullname.value)
    #     showvalues.append(self.inputs.email.value)
    #     showvalues.append(self.inputs.username.value)
    #     showvalues.append(self.inputs.password.value)
    #     showvalues.append(self.inputs.passwordv.value)
    #     return showvalues
        
    def generate_ssh(self):
        try:
            self.validate.check_all(self.inputs)
        except UserInputError as e:
            display(Javascript(
                "alert('%s')" %e
            ))
            raise e
        # display(getattr(self.inputs, 'email').value)
        self.ssh_params = self.ssh.execute(getattr(self.inputs, 'email').value) #get from InputNameMap
        
    def get_ssh_params(self):
        return self.ssh_params
    
    def configure_git(self):
        self.git.configure(
            getattr(self.inputs, 'username').value, getattr(self.inputs, 'fullname').value, getattr(self.inputs, 'email').value
        )
        self.git.setup_repository()
  
@dataclass
class InputNameMap:
    USERNAME: str = 'username'
    FULLNAME: str = 'fullname'
    EMAIL: str = 'email'
    PASSWORD: str = 'password'
    PASSWORD_V: str = 'passwordv'
        
class InputValidation:
    def __init__(self, inputs_map: InputNameMap):
        self.inputs_map = inputs_map
        
    def all_attributes_missing(self, inputs):
        attributes = [
            self.inputs_map.USERNAME, self.inputs_map.FULLNAME, self.inputs_map.EMAIL, self.inputs_map.PASSWORD, self.inputs_map.PASSWORD_V
        ]
        count = 0
        for attr in attributes:
            if self.is_attribute_empty(inputs, attr):
                count = count + 1

        if count == len(attributes):
            raise UserInputError("Please fill in the form with your info")

    def username(self, inputs):
        if self.is_attribute_empty(inputs, self.inputs_map.USERNAME):
            raise UserInputError("Please provide your username")

    def email(self, inputs):
        if self.is_attribute_empty(inputs, self.inputs_map.EMAIL):
            raise UserInputError("Please provide your email")

    def fullname(self, inputs):
        if self.is_attribute_empty(inputs, self.inputs_map.FULLNAME):
            raise UserInputError("Please provide your full name")

    def password(self, inputs):
        if self.is_attribute_empty(inputs, self.inputs_map.PASSWORD):
            raise UserInputError("Please provide your password")

    def passwordv(self, inputs):
        if self.is_attribute_empty(inputs, self.inputs_map.PASSWORD_V):
            raise UserInputError("Please provide your password again")

    def check_password_match(self, inputs):
        if self.if_attribute_mismatch(inputs, self.inputs_map.PASSWORD, self.inputs_map.PASSWORD_V):
            raise UserInputError("Please make sure your passwords match")

    def if_attribute_mismatch(self, inputs, attribute1, attribute2):
        if getattr(inputs, attribute1).value != getattr(inputs, attribute2).value:
            return True

        return False

    def is_attribute_empty(self, inputs, attribute: str):
        if  getattr(inputs, attribute).value == '':
            return True

        return False

    def check_all(self, inputs):
        self.all_attributes_missing(inputs) 
        #Checks if all attributes are missing from form and returns "Please fill in form".
        self.email(inputs) #checks if email is missing
        self.fullname(inputs) #same as above but for name
        self.username(inputs)
        self.password(inputs)
        self.passwordv(inputs)
        self.check_password_match(inputs) #cmon
        
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
        
        return InputValueMap(fullname, email, username, password1, password2)
    
class SSH_Setup:
    def __init__(self, root_folder: str):
        self.root_folder = root_folder
        
    def generate_for(self, email_address: str):
        cmd2 = os.system("rm -rf %s/.ssh/id* %s/.ssh/.id*" % (self.root_folder, self.root_folder))
        md2 = os.system("yes '' | ssh-keygen -N '' -C '%s' > /dev/null" % (email_address))
        
        # key = self.read_ssh_key()
        # js = self.create_js_for_ssh_key(key)
        # display(Javascript(js))
        return SSHParams(email_address, key)
        
    def get_key(self):
        return self.key
    
#     def get_js(self):
#         return self.js

    # def read_ssh_key(self):
    #     with open('/home/saxenap/.ssh/id_rsa.pub', 'r') as file:
    #         return file.read().strip()
        
        # cmd1 = os.system("chmod 600 /home/saxenap/.ssh/id_rsa")

#     def create_js_for_ssh_key(self, key):
#         key = key.strip()
#         return \
# """function copyToClipboard(text) {
# window.prompt("Copy to clipboard: Ctrl+C, Enter", text);
# }
# copyToClipboard('%s'); """ % key
    
#     def display_js(self):
#         display(Javascript(self.js))
        
        
        
class GitUserConfiguration:
    def configure_for(self, username, fullname, email):
        cmd2_1 = os.system("git config --global user.name '%s'" % fullname)
        cmd2_2 = os.system("git config --global user.email '%s'" % email)
        cmd2_2 = os.system("git config --global credential.username '%s'" % username)
        

class GitRepositoryConfiguration:     
    def configure_for(self, repo_ssh_url: str, local_dir_path: str):
        cmd1 = os.system("cd %s" % local_dir_path)
        cmd3 = os.system("git clone git@gitlab.hubzero.org:saxenap/nanohub-analytics.git temp")
        

class JupyterPasswordConfiguration:
    def configure_for(self, password: str):

@dataclass
class OnboardingCommand:
    fullname: str 
    email: str
    username: str 
    jupyter_password: str
    repo_ssh_url: str = 'git@gitlab.hubzero.org:saxenap/nanohub-analytics.git'
    local_dir_path: str = '/home/saxenap'
    
    
class IOnboardingCommandMapper:
    def create_new(self) -> OnboardingCommand:
        raise NotImplementedError

        
class JupyterCommandMapper(IOnboardingCommandMapper):
    def __init__(self, form):
        self.form = form
        
    def create_new(self) -> OnboardingCommand:
        inputs = self.form.execute()
        return OnboardingCommand(
            inputs.fullname.value,
            inputs.email.value,
            inputs.username.value,
            inputs.password.value
        )
    
    
class CommandErrors:
    def __init__(self):
        self.errors_by_key = {}
    
    def set_error_for(self, key: str, error: str) -> None:
        self.errors_by_key[key] = error
    
    def get_errors(self) -> {}:
        return self.errors_by_key
    
    def has_errors(self) -> bool:
        return not self.errors_by_key
    
    
class CommandValidator:
    def __init__(self, errors: CommandErrors):
        self.errors = errors
        
    def validate(self, command: OnboardingCommand) -> CommandErrors:
        
        #fullname
        if command.fullname == "":
            self.errors.set_error_for('name', 'Full name field is empty!')
            
        #email
        
#         regexforemail = r'(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\' + \
#             'x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z' + \
#             '0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-' +\
#             '9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08' +\
#             '\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'

#         if !(re.fullmatch(regexforemail, command.email)):
#             self.errors.set_error_for('email', 'Email is not valid!')
        
        if command.email == "":
            self.errors.set_error_for('email', 'Email field is empty!')
            
        #username
        if command.fullname == "":
            self.errors.set_error_for('name', 'Username field is empty!')
            
        #jupyterpassword
        if command.jupyter_password == "":
            self.errors.set_error_for('password', 'Jupyter password field is empty!')
        
        return self.errors

    
class OnboardingProcessor:
    def __init__(
        self, 
        validator: CommandValidator,
        ssh: SSH_Setup, 
        git_user: GitUserConfiguration, 
        git_repo: GitRepositoryConfiguration,
        jupyter_password: JupyterPasswordConfiguration
    ):
        self.validator = validator
        self.ssh = ssh
        self.git_user = git_user
        self.git_repo = git_repo
        self.jupyter_password = jupyter_password
                
    
    def process(self, command: OnboardingCommand) -> None:
        errors = self.validate(command)
        if errors.has_errors():
            raise UserInputError(json.dumps(errors.get_errors()))
            
        self.git_user.configure_for(
            command.username,
            command.fullname,
            command.email
        )
        self.ssh.generate_for(email_address)
        self.git_repo.configure_for(
            command.repo_ssh_url,
            command.local_dir_path
        )
        self.jupyter_password.configure_for(command.jupyter_password)
        
    
