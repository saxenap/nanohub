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
    def __init__(self, credentials: dict, scopes: str, service_type: str, version: str):
        self.credentials = credentials
        self.scopes = scopes
        self.service_type = service_type
        self.version = version

    def create_new_service(self):
        json_key = json.loads(
            json.dumps(self.credentials), strict=False
        )

        credentials = Credentials.from_service_account_info(
            json_key, scopes=self.scopes.split(",")
        )

        return build(self.service_type, self.version, credentials=credentials, cache_discovery=False)


class GoogleApiContainer(containers.DeclarativeContainer):

    config = providers.Configuration()

    credentials_dict = providers.Dict({
        'type': config.googleapi.type,
        'project_id': config.googleapi.project_id,
        'private_key_id': config.googleapi.private_key_id,
        'private_key': config.googleapi.private_key,
        'client_email': config.googleapi.client_email,
        'client_id': config.googleapi.client_id,
        'auth_uri': config.googleapi.auth_uri,
        'token_uri': config.googleapi.token_uri,
        'auth_provider_x509_cert_url': config.googleapi.auth_provider_x509_cert_url,
        'client_x509_cert_url': config.googleapi.client_x509_cert_url
    })

    googleapi_service = providers.Factory(
        GoogleApiFactory,
        credentials_dict,
        config.googleapi.scopes,
        config.googleapi.service_type,
        config.googleapi.service_version
    )


