from pydantic import BaseSettings, Field
from dotenv import load_dotenv


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

    grant_type: str = Field(env='salesforce_grant_type')
    client_id: str = Field(env='salesforce_client_id')
    client_secret: str = Field(env='salesforce_client_secret')
    username: str = Field(env='salesforce_username')
    password: str = Field(env='salesforce_password')


class GoogleApiSettings(BaseSettings):

    type: str = Field(env='google_account_type')
    project_id: str = Field(env='google_project_id')
    private_key_id: str = Field(env='google_private_key_id')
    private_key: str = Field(env='google_private_key')
    client_email: str = Field(env='google_client_email')
    client_id: str = Field(env='google_client_id')
    auth_uri: str = Field(env='google_auth_uri')
    token_uri: str = Field(env='google_token_uri')
    auth_provider_x509_cert_url: str = Field(env='google_auth_provider_x509_cert_url')
    client_x509_cert_url: str = Field(env='google_client_x509_cert_url')
    scopes: str = Field(env='google_scopes')
    service_type: str = Field(env='google_api_service_type')
    service_version: str = Field(env='google_api_service_version')



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
    pathsettings: PathSettings = PathSettings()
    executorsettings: ExecutorSettings = ExecutorSettings()
#     remoteservicessettings: RemoteServicesSettings = RemoteServicesSettings()