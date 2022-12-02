# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 6/24/22
import logging
from dataclasses import dataclass
from memory_profiler import memory_usage
import logging
import json
import time
from datetime import datetime
from nanoHUB.logger import LoggerMixin


@dataclass
class ICommand:
    log_level: str

    def __post_init__(self):
        self.init_datetime = datetime.now().isoformat()

    def init_datetime(self) -> str:
        return self.init_datetime

    @property
    def command_name(self) -> str:
        return self.__class__.__name__

    def __repr__(self):
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError


class ICommandHandler:
    handler_name: str = ''

    def handle(self, command: ICommand) -> None:
        raise NotImplementedError

    def get_handler_name(self) -> str:
        return self.handler_name


class NullCommandHandler(ICommandHandler):
    handler_name: str = 'Null Handler'
    def handle(self, command: ICommand) -> None:
        return


class InitialExecutionDecorator(ICommandHandler, LoggerMixin):
    handler_name: str = 'Initial Execution Handler'

    def __init__(self, inner_handler: ICommandHandler):
        self.inner_handler = inner_handler

    def handle(self, command: ICommand) -> None:
        self.logger.debug(
            "%s has started." % self.inner_handler.get_handler_name()
        )
        self.inner_handler.handle(command)
        self.logger.debug(
            "%s has finished."
        )


class IMetricsReporter:
    def report(self, handler: ICommandHandler, command: ICommand) -> dict:
        raise NotImplemented


class TimingProfileReporter(IMetricsReporter):
    def report(self, handler: ICommandHandler, command: ICommand) -> dict:
        start_time = time.time()
        handler.handle(command)
        return {"ExecutionTime (s)": time.time() - start_time}


class MemoryProfileReporter(IMetricsReporter):
    def report(self, handler: ICommandHandler, command: ICommand) -> dict:
        mem_usage = memory_usage((handler.handle, (command, )), max_usage=True, include_children=True)
        return {"MemoryUsed (MiB)": mem_usage}


class MetricsReporterDecorator(ICommandHandler, LoggerMixin):
    def __init__(
        self, inner_handler: ICommandHandler, metrics_reporters: [IMetricsReporter]
    ):
        self.inner_handler = inner_handler
        self.metrics_reporters = metrics_reporters

    def handle(self, command: ICommand) -> None:
        result = {'task': self.get_handler_name(), 'metrics': {}}

        for reporter in self.metrics_reporters:
            result['metrics'].update(reporter.report(self.inner_handler, command))

        self.logger.info(json.dumps(result))