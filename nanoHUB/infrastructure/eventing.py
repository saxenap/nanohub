# Created by saxenap at 6/1/22


class IEvent:
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
    def __init__(self, handlers: []):
        self.handlers = []

    def add_handler(self, handler: IEventHandler) -> None:
        self.handlers.append(handler)

    def notify_for(self, event: IEvent) -> None:
        for handler in self.handlers:
            handler.handle(event)

