# Created by saxenap at 6/24/22
import logging
from dataclasses import dataclass
from memory_profiler import memory_usage
import logging
import json
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
    def handle(self, command: ICommand) -> None:
        raise NotImplementedError

    def get_name(self) -> str:
        raise NotImplementedError


class NullCommandHandler(ICommandHandler):
    def handle(self, command: ICommand) -> None:
        return

    def get_name(self) -> str:
        return 'Null Command Handler'


class InitialExecutionDecorator(ICommandHandler):
    def __init__(self, inner_handler: ICommandHandler, logger: logging.Logger):
        self.inner_handler = inner_handler
        self.logger = logger

    def handle(self, command: ICommand) -> None:
        self.logger.debug(
            "%s has started." % self.inner_handler.get_name()
        )
        self.inner_handler.handle(command)
        self.logger.debug(
            "%s has finished."
        )

    def get_name(self) -> str:
        return 'Initial Execution Handler'


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


class MetricsReporterDecorator(ICommandHandler):
    def __init__(
        self, inner_handler: ICommandHandler, metrics_reporters: [IMetricsReporter], logger: logging.Logger
    ):
        self.inner_handler = inner_handler
        self.metrics_reporters = metrics_reporters
        self.logger = logger

    def handle(self, command: ICommand) -> None:
        result = {'task': self.get_name(), 'metrics': {}}

        for reporter in self.metrics_reporters:
            result['metrics'].update(reporter.report(self.inner_handler, command))

        self.logger.info(json.dumps(result))

    def get_name(self) -> str:
        return self.inner_handler.get_name()