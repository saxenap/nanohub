# Created by saxenap at 6/13/22
from datetime import datetime


class Session:
    def get_user(self) -> 'User':
        return self.user

    def get_datetime(self) -> datetime:
        return self.datetime


class User:
    def get_last_session(self) -> Session:
        return self.last_session

    def get_first_session(self) -> Session:
        return self.first_session



