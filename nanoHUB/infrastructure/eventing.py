# Created by saxenap at 6/1/22

class IEvent:
    def __repr__(self) -> str:
        raise NotImplementedError


class IEventHandler:
    def handle(self, event: IEvent):
        raise NotImplementedError


class EventNotifier:
    def __init__(self):
        self.handlers = []

    def add_handler(self, handler: IEventHandler) -> None:
        self.handlers.append(handler)

    def notify_for(self, event: IEvent) -> None:
        for handler in self.handlers:
            handler.handle(event)