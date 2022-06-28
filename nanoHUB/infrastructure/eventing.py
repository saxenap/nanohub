# Created by saxenap at 6/1/22
import time
from datetime import datetime
from dataclasses import dataclass


@dataclass
class IEvent:
    command_name: str
    command_datetime: str

    def __post_init__(self):
        self.init_datetime = datetime.now().isoformat()

    def init_datetime(self) -> str:
        return self.init_datetime

    @classmethod
    def get_event_name(cls) -> str:
        return cls.__name__

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class IEventHandler:
    def handle(self, event):
        raise NotImplementedError


class EventNotifier:
    def __init__(self):
        self.event_handlers = {}

    def add_event_handler(self, event_name: str, handler: IEventHandler) -> None:
        if event_name not in self.event_handlers:
            self.event_handlers[event_name] = []
        self.event_handlers[event_name].append(handler)

    def notify_for(self, event: IEvent) -> None:
        event_name = event.get_event_name()
        print(event)
        print(event_name)
        if event_name in self.event_handlers:
            handlers = self.event_handlers[event_name]
            for handler in handlers:
                handler.handle(event)


class IFilePathProvider:
    def append_path(self, path: str) -> None:
        raise NotImplementedError

    def file_path_for_event(self, event: IEvent) -> str:
        raise NotImplementedError


class FilePathByCommandDatetime(IFilePathProvider):
    def __init__(self, file_path_prefix: str = '', format: str = "%Y-%m-%d--%H-%M-%S"):
        self.prefix = file_path_prefix
        self.format = format

    def append_path(self, path: str) -> None:
        self.prefix = self.prefix + '/' + path

    def file_path_for_event(self, event: IEvent) -> str:
        event_dt = datetime.fromisoformat(event.command_datetime)
        return self.prefix + '/' + \
               str(event_dt.year) + '/' + \
               str(event_dt.month) + '/' + \
               str(event_dt.day) + '/' + \
               event_dt.strftime(self.format)