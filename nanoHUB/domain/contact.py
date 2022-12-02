# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 5/24/22
from dataclasses import dataclass, field
from datetime import datetime
import json


class IContactName:
    def get_title(self) -> str:
        raise NotImplementedError

    def get_first_name(self) -> str:
        raise NotImplementedError

    def get_middle_name(self) -> str:
        raise NotImplementedError

    def get_last_name(self) -> str:
        raise NotImplementedError

    def get_full_name(self) -> str:
        raise NotImplementedError


class ContactName(IContactName):
    def __init__(self, full_name: str, title: str, first_name: str, middle_name: str, last_name: str):
        self.full_name = full_name
        self.title = title
        self.first_name = first_name
        self.last_name = last_name
        self.middle_name = middle_name

    def get_title(self) -> str:
        return self.title

    def get_first_name(self) -> str:
        return self.first_name

    def get_middle_name(self) -> str:
        return self.middle_name

    def get_last_name(self) -> str:
        return self.last_name

    def get_full_name(self) -> str:
        return self.full_name

    def __str__(self) -> str:
        return json.dumps(vars(self))


@dataclass
class ContactParams:
    id: str
    username: str
    email: str
    registration_date: datetime
    last_active_date: datetime
    name: ContactName
    meta: dict = field(default_factory=lambda: {})

    def get_full_name(self) -> str:
        return self.name.get_full_name()

    def __str__(self) -> str:
        return json.dumps(vars(self))


class ContactNotCreated(RuntimeError):
    def get_errors(self) -> []:
        raise NotImplementedError

    def get_params(self) -> ContactParams:
        raise NotImplementedError


class Contact:
    def __init__(self, params: ContactParams):
        self.params = params

    def get_id(self) -> str:
        return self.params.id

    def get_username(self) -> str:
        return self.params.username

    def get_email(self) -> str:
        return self.params.email

    def get_name(self) -> str:
        return self.params.get_full_name()

    def add_meta(self, key: str, value):
        self.params.meta[key] = value

    def __str__(self) -> str:
        return json.dumps(vars(self))