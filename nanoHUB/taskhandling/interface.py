from logging import Logger
from datetime import datetime
import time
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ITaskParameters:
    name: str
    index: int
    create_at: datetime = field(default=str(datetime.now()))

    def get_task_name(self) -> str:
        return self.name

    def get_id(self) -> int:
        return self.index

    def create_date_time(self) -> datetime:
        return self.create_at


import pprint
import json
params = ITaskParameters('name', 12)
pprint.pprint((params))
import time
time.sleep(10)
pprint.pprint((params))

class ITaskHandler:
    def execute(self, task: ITaskParameters) -> 'ITaskParameters':
        raise NotImplementedError


class ProfilingHandler(ITaskHandler):
    def __init__(self, handler: ITaskHandler, logger: Logger):
        self.handler = handler
        self.logger = logger

    def execute(self, task: ITaskParameters) -> 'ITaskParameters':
        start_time = time.time()
        self.handler.execute(task)
        self.logger.info("Executing task % took %s", task.get_task_name(), time.time() - start_time)
        return task


class FakeHandler(ITaskHandler):
    def execute(self, task: ITaskParameters) -> 'ITaskParameters':
        return task


class DebugLoggingHandler(ITaskHandler):
    def __init__(self, handler: ITaskHandler, logger: Logger):
        self.handler = handler
        self.logger = logger

    def execute(self, task: ITaskParameters) -> 'ITaskParameters':
        self.logger.info("About to handle task %d (%s) created at %s", task.get_id(), task.get_task_name(), task.create_date_time())
        self.handler.execute(task)
        self.logger.info("Executing task % took %s", task.get_task_name())
        return task


