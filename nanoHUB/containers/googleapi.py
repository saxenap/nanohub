from dependency_injector import containers, providers
from nanoHUB.dataaccess.connection import DbConnectionParams, PyMysqlConnectionFactory, TunneledConnectionParams, TunneledConnectionFactory
from nanoHUB.dataaccess.connection import SqlAlchemyConnectionFactory
from nanoHUB.logger import logger
from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import AuthorizedSession
from httplib2 import Http
import logging
import json


class GoogleApiFactory:
    def __init__(self, credentials_file_path: str, scopes: str, service_type: str, version: str):
        self.credentials_file_path = credentials_file_path
        self.scopes = scopes
        self.service_type = service_type
        self.version = version

    def create_new_service(self, root_dir: str):
        credentials_file_path = root_dir + '/' + self.credentials_file_path
        with open(credentials_file_path) as f:
            json_key = json.load(f)

        credentials = Credentials.from_service_account_info(
            json_key, scopes=self.scopes.split(",")
        )

        return build(self.service_type, self.version, credentials=credentials, cache_discovery=False)


class GoogleApiContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    googleapi_service = providers.Factory(
        GoogleApiFactory,
        config.googleapi.credentials_file_path,
        config.googleapi.scopes,
        config.googleapi.service_type,
        config.googleapi.service_version
    )


