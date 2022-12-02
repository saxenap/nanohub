# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 5/23/22
import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build


class ServiceFactory:
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
