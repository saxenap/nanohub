# Created by saxenap at 5/25/22

from nameparser import HumanName
from nanoHUB.domain.contact import ContactName


class NameParser:
    def __init__(self, name: HumanName):
        self.name = name

    def get_title(self) -> str:
        return self.name.title

    def get_first_name(self) -> str:
        return self.name.first

    def get_middle_name(self) -> str:
        return self.name.middle

    def get_last_name(self) -> str:
        return self.name.last

    def get_full_name(self) -> str:
        return str(self.name)


class NameParserFactory:
    def parse_from(self, full_name: str) -> NameParser:
        return NameParser(HumanName(full_name))