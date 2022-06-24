# Created by saxenap at 5/24/22
from nanoHUB.domain.contact import (
    Contact,
    ContactParams,
    ContactNotCreated,
    ContactName
)
from simple_salesforce import Salesforce
from dataclasses import dataclass
import json
import os


@dataclass
class ContactMappings:
    id: str = 'nanoHUB_user_ID__c'
    username: str = 'nanoHUB_username__c'
    email: str = 'Email'
    registration_date: str = 'nanoHUB_registration_date__c'
    last_active_date: str = 'nanoHUB_last_active_date__c'
    usertype: str = 'Organization_Type__c'
    salutation: str = 'Salutation__c'
    name: str = 'Name'
    first_name: str = 'FirstName'
    middle_name: str = 'MiddleName'
    last_name: str = 'LastName'
    blocked: str = 'nanoHUB_account_BLOCKED__c'
    has_opted_out_of_email: str = 'HasOptedOutOfEmail'


@dataclass
class SimpleSalesforceFactory:
    username: str
    password: str
    security_token: str
    client_id: str
    domain: str

    def create_new_engine(self):
        return Salesforce(
            self.username,
            self.password,
            self.security_token,
            self.client_id,
            self.domain
        )


class ContactFactory:
    def construct_from(self, result: dict) -> Contact:
        return Contact(ContactParams(
            result[ContactMappings.id],
            result[ContactMappings.username],
            result[ContactMappings.email],
            result[ContactMappings.registration_date],
            result[ContactMappings.last_active_date],
            ContactName(
                result[ContactMappings.name],
                result[ContactMappings.salutation],
                result[ContactMappings.first_name],
                result[ContactMappings.middle_name],
                result[ContactMappings.last_name]
            ),
            {'salesforce_id': result['Id']}
        ))


class ContactMapper:
    def __init__(self, engine: Salesforce, factory: ContactFactory):
        self.engine = engine
        self.factory = factory

    def get_fields(self) -> []:
        desc = self.engine.Contact.describe()
        return [field['name'] for field in desc['fields']]

    def find_by_email(self, email: str) -> Contact:
        result = self.engine.Contact.get_by_custom_id(
            ContactMappings.email, email
        )
        return self.factory.construct_from(result)

    def find_by_username(self, username: str) -> Contact:
        result = self.engine.Contact.get_by_custom_id(
            ContactMappings.username, username
        )
        return self.factory.construct_from(result)

    def find_by_id(self, nanohub_id: str) -> Contact:
        result = self.engine.Contact.get_by_custom_id(
            ContactMappings.id, nanohub_id
        )
        return self.factory.construct_from(result)

    def find_by_(self, key: str, salesforce_id: str) -> Contact:
        result = self.engine.Contact.get_by_custom_id(
            key, salesforce_id
        )
        return self.factory.construct_from(result)

    def save(self, contact: Contact) -> Contact:
        params = contact.params
        result = self.engine.Contact.create({
            ContactMappings.id: params.id,
            ContactMappings.email: params.email,
            ContactMappings.registration_date: params.registration_date,
            ContactMappings.last_active_date: params.last_active_date
        })

        if result.success:
            return self.find_by_salesforce_id(result.id)

        raise SalesforceContactNotCreated(result.errors, params)


class SalesforceContactNotCreated(ContactNotCreated):
    def __init__(self, errors: [], params: ContactParams):
        super().__init__(json.dumps(errors.errors))
        self.errors = errors
        self.params = params

    def get_errors(self) -> []:
        return self.errors

    def get_params(self) -> ContactParams:
        return self.params


class SalesforceFromEnvironment:
    def __init__(self, domain: str, prefix: str = 'salesforce_'):
        self.prefix = prefix
        self.domain = domain

    def create_new(self) -> Salesforce:
        factory = SimpleSalesforceFactory(
            os.environ['%susername' % self.prefix],
            os.environ['%spassword' % self.prefix],
            os.environ['%ssecurity_token' % self.prefix],
            os.environ['%sclient_id' % self.prefix],
            self.domain
        )
        return factory.create_new_engine()