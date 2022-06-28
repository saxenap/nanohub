# Created by saxenap at 6/24/22
from simple_salesforce import Salesforce, SalesforceLogin
from dataclasses import dataclass
import os
from nanoHUB.pipeline.salesforce.DB2SalesforceAPI import DB2SalesforceAPI


class ISalesforceFactory:
    def create_new(self) -> Salesforce:
        raise NotImplementedError


@dataclass
class LoginBySecurityTokenParams(ISalesforceFactory):
    grant_type: str
    username: str
    password: str
    security_token: str
    client_id: str
    client_secret: str
    domain: str

    def create_new(self) -> Salesforce:
        client = DB2SalesforceAPI({
            'grant_type': self.grant_type,
            'username': self.username,
            'password': self.password,
            'security_token': self.security_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret
        })
        session_id = client.get_access_token()
        instance_url = client.get_instance_url()
        return Salesforce(
            domain=self.domain, session_id=session_id, instance_url=instance_url
        )


class SalesforceFromEnvironment(ISalesforceFactory):
    def __init__(self, domain: str, prefix: str = 'salesforce_'):
        self.domain = domain
        self.prefix = prefix

    def create_new(self) -> Salesforce:
        login = LoginBySecurityTokenParams(
            os.environ['%sgrant_type' % self.prefix],
            os.environ['%susername' % self.prefix],
            os.environ['%spassword_with_token' % self.prefix],
            os.environ['%ssecurity_token' % self.prefix],
            os.environ['%sclient_id' % self.prefix],
            os.environ['%sclient_secret' % self.prefix],
            self.domain
        )
        return login.create_new()

