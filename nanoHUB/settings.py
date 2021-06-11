from pydantic import BaseSettings, Field
from dotenv import load_dotenv


load_dotenv()
class DatabaseSettings(BaseSettings):

    host: str = Field(env='db_host')
    user: str = Field(env='db_user')
    password: str = Field(env='db_password')


class SshTunnel(BaseSettings):

    use_ssh_connection: str = Field(env='tunnel_use_ssh_connection')
    host: str = Field(env='tunnel_ssh_host')
    username: str = Field(env='tunnel_ssh_username')
    password: str = Field(env='tunnel_ssh_password')
    port: str = Field(env='tunnel_ssh_port')
    remote_bind_address: str = Field(env='tunnel_remote_bind_address')
    remote_bind_port: str = Field(env='tunnel_remote_bind_port')


class SalesforceSettings(BaseSettings):

    grant_type: str = Field(env='salesforce_grant_type')
    client_id: str = Field(env='salesforce_client_id')
    client_secret: str = Field(env='salesforce_client_secret')
    username: str = Field(env='salesforce_username')
    password: str = Field(env='salesforce_password')


class PathSettings(BaseSettings):

    outfile_dir: str = Field(env='pipeline_outfile_dir')


class ExecutorSettings(BaseSettings):

    max_retries_on_failure: int = Field(env='executor_max_retries_on_failure')


class Settings(BaseSettings):

    database: DatabaseSettings = DatabaseSettings()
    sshtunnel: SshTunnel = SshTunnel()
    salesforce: SalesforceSettings = SalesforceSettings()
    pathsettings: PathSettings = PathSettings()
    executorsettings: ExecutorSettings = ExecutorSettings()