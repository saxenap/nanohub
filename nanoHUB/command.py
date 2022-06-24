# Created by saxenap at 6/24/22
from dataclasses import dataclass
import time


@dataclass
class ICommand:
    datetime: str

    def __init__(self):
        self.datetime = time.strftime("%Y%m%d-%H%M%S")

    def get_name(self) -> str:
        raise NotImplementedError

    def get_datetime(self) -> str:
        return self.datetime

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class ICommandHandler:
    def execute(self, command) -> None:
        raise NotImplementedError
