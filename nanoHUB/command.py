# Created by saxenap at 6/24/22
from dataclasses import dataclass


@dataclass
class ICommand:
    def get_name(self) -> str:
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class ICommandHandler:
    def execute(self, command) -> None:
        raise NotImplementedError
