from pydantic import BaseSettings, Field
import pathlib


class DatabaseSettings(BaseSettings):

    class Config:
        env_file = pathlib.Path(__file__).parent.absolute() / '.env'
        env_file_encoding = 'utf-8'

    host: str = Field(env='db_host')
    user: str = Field(env='db_user')
    password: str = Field(env='db_password')


class SshTunnel(BaseSettings):

    class Config:
        env_file = pathlib.Path(__file__).parent.absolute() / '.env'
        env_file_encoding = 'utf-8'

    use_ssh_connection: str = Field(env='tunnel_use_ssh_connection')
    host: str = Field(env='tunnel_ssh_host')
    username: str = Field(env='tunnel_ssh_username')
    password: str = Field(env='tunnel_ssh_password')
    port: str = Field(env='tunnel_ssh_port')
    remote_bind_address: str = Field(env='tunnel_remote_bind_address')
    remote_bind_port: str = Field(env='tunnel_remote_bind_port')


class SalesforceSettings(BaseSettings):

    class Config:
        env_file = pathlib.Path(__file__).parent.absolute() / '.env'
        env_file_encoding = 'utf-8'

    grant_type: str = Field(env='salesforce_grant_type')
    client_id: str = Field(env='salesforce_client_id')
    client_secret: str = Field(env='salesforce_client_secret')
    username: str = Field(env='salesforce_username')
    password: str = Field(env='salesforce_password')


class Settings(BaseSettings):

    database: DatabaseSettings = DatabaseSettings()
    sshtunnel: SshTunnel = SshTunnel()
    salesforce: SalesforceSettings = SalesforceSettings()

