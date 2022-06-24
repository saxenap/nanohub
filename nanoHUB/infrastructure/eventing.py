# Created by saxenap at 6/1/22
import time


class IEvent:
    event_datetime: str

    def __init__(self):
        self.datetime = time.strftime("%Y%m%d-%H%M%S")

    def get_event_datetime(self):
        return self.event_datetime

    def get_event_name(self) -> str:
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class IEventHandler:
    def handle(self, event):
        raise NotImplementedError


class EventNotifier:
    def __init__(self, event_handlers: [] = []):
        self.event_handlers = event_handlers

    def add_event_handler(self, handler: IEventHandler) -> None:
        self.event_handlers.append(handler)

    def notify_for(self, event: IEvent) -> None:
        for handler in self.event_handlers:
            handler.handle(event)

