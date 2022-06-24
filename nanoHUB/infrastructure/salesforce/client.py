# Created by saxenap at 6/24/22
from simple_salesforce import Salesforce
from dataclasses import dataclass
import os


class ISalesforceFactory:
    def create_new(self) -> Salesforce:
        raise NotImplementedError


@dataclass
class SimpleSalesforceFactory(ISalesforceFactory):
    username: str
    password: str
    security_token: str
    client_id: str
    domain: str

    def create_new(self) -> Salesforce:
        return Salesforce(
            self.username,
            self.password,
            self.security_token,
            self.client_id,
            self.domain
        )


class SalesforceFromEnvironment(ISalesforceFactory):
    def __init__(self, domain: str, prefix: str = 'salesforce_'):
        self.domain = domain
        self.prefix = prefix

    def create_new(self) -> Salesforce:
        params = SimpleSalesforceFactory(
            os.environ['%susername' % self.prefix],
            os.environ['%spassword' % self.prefix],
            os.environ['%ssecurity_token' % self.prefix],
            os.environ['%sclient_id' % self.prefix],
            self.domain
        )
        return params.create_new()