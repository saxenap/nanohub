from pydantic import BaseSettings, Field
from dotenv import load_dotenv
from typing import Optional


load_dotenv()
class DatabaseSettings(BaseSettings):

    host: str = Field(env='db_host')
    user: str = Field(env='db_user')
    password: str = Field(env='db_password')
    charset: str = Field(env='db_charset')


class SshTunnel(BaseSettings):

    use_ssh_connection: str = Field(env='tunnel_use_ssh_connection')
    host: str = Field(env='tunnel_ssh_host')
    username: str = Field(env='tunnel_ssh_username')
    password: str = Field(env='tunnel_ssh_password')
    port: str = Field(env='tunnel_ssh_port')
    remote_bind_address: str = Field(env='tunnel_remote_bind_address')
    remote_bind_port: str = Field(env='tunnel_remote_bind_port')


class SalesforceSettings(BaseSettings):

    grant_type: Optional[str] = Field(env='salesforce_grant_type')
    client_id: Optional[str] = Field(env='salesforce_client_id')
    client_secret: Optional[str] = Field(env='salesforce_client_secret')
    username: Optional[str] = Field(env='salesforce_username')
    password: Optional[str] = Field(env='salesforce_password')


class GoogleApiSettings(BaseSettings):

    credentials_file_path: Optional[str] = Field(env='google_credentials_file_path')
    scopes: Optional[str] = Field(env='google_scopes')
    service_type: Optional[str] = Field(env='google_api_service_type')
    service_version: Optional[str] = Field(env='google_api_service_version')


class GeddesApiSettings(BaseSettings):

    endpoint: Optional[str] = Field(env='geddes_endpoint')
    username: Optional[str] = Field(env='geddes_user')
    access_key: Optional[str] = Field(env='geddes_access_key')
    secret_key: Optional[str] = Field(env='geddes_secret_key')


class PathSettings(BaseSettings):

    outfile_dir: str = Field(env='pipeline_outfile_dir')


class ExecutorSettings(BaseSettings):

    max_retries_on_failure: int = Field(env='executor_max_retries_on_failure')


# class RemoteServicesSettings(BaseSettings):

#     papertrail_hostname: str = Field(env='papertrail_hostname')
#     papertrail_port: int = Field(env='papertrail_port')

class Settings(BaseSettings):

    database: DatabaseSettings = DatabaseSettings()
    sshtunnel: SshTunnel = SshTunnel()
    salesforce: SalesforceSettings = SalesforceSettings()
    googleapi: GoogleApiSettings = GoogleApiSettings()
    geddesapi: GeddesApiSettings = GeddesApiSettings()
    pathsettings: PathSettings = PathSettings()
    executorsettings: ExecutorSettings = ExecutorSettings()
#     remoteservicessettings: RemoteServicesSettings = RemoteServicesSettings()