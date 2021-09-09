import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import papermill
from memory_profiler import memory_usage
import logging
from pathlib import Path
import subprocess
import os
import json
import time


class IExecutor:

    def __call__(self):
        raise NotImplemented

    def get_name(self) -> str:
        raise NotImplemented


class JupyterExecutor(IExecutor):

    def __init__(self, notebook_path: str, outfile_path: str, logger: logging.Logger):
        self.notebook_path = notebook_path
        self.outfile_path = outfile_path
        self.logger = logger

    def __call__(self):

        if not os.path.isdir(self.outfile_path):
            Path(self.outfile_path).mkdir(parents=True, exist_ok=True)
            raise RuntimeError("Output file dir %s not found." % self.outfile_path)

        output_file_path = self.outfile_path + '/' + Path(self.notebook_path).name

        papermill.execute_notebook(
            self.notebook_path,
            output_file_path,
            log_output=True,
            report_mode=True
        )
        self.logger.info('Saved output file - %s' % output_file_path)

    def get_name(self) -> str:
        return '%s'% self.notebook_path


class PythonFileExecutor(IExecutor):

    def __init__(self, file_path: str, logger: logging.Logger):
        self.file_path = file_path
        self.logger = logger

    def __call__(self):
        locals = {}
        globals = {}
        globals.update({
            "__file__": self.file_path,
            "__name__": "__main__",
        })
        with open(self.file_path, 'rb') as file:
            exec(compile(file.read(), self.file_path, 'exec'), globals, locals)

    def get_name(self) -> str:
        return '%s'% self.file_path


class RFileExecutor(IExecutor):

    def __init__(self, r_executable_path: str, file_path: str, outfile_path: str, logger: logging.Logger):
        self.file_path = file_path
        self.r_executable_path = r_executable_path
        self.outfile_path = outfile_path
        self.logger = logger

    def __call__(self):
        subprocess.call([self.r_executable_path, "--vanilla", self.file_path])

    def get_name(self) -> str:
        return '%s'% self.file_path

'''
##################################################################################################

Decorating Executors

##################################################################################################
'''


class RetryingExecutorDecorator(IExecutor):

    def __init__(self, executor: IExecutor, retries_max_count: int, logger: logging.Logger):
        self.executor = executor
        self.retries_max_count = retries_max_count
        self.retries_current_count = 0
        self.logger = logger

    def __call__(self):
        for i in range(0, self.retries_max_count):
            try:
                self.logger.info("Attempt %d of %d [%s]." % (
                    i+1, self.retries_max_count, self.get_name()
                ))
                self.executor()
                return
            except Exception as excep:
                self.logger.error("FAILURE [%s] - %s." % (
                    self.get_name(), excep
                ))
                if i < self.retries_max_count:
                    self.logger.info("RETRYING [%s]" % self.get_name())
                continue


    def get_name(self) -> str:
        return self.executor.get_name()


class IMetricsReporter:

    def report(self, executor: IExecutor) -> dict:
        raise NotImplemented


class TimingProfileReporter(IMetricsReporter):

    def report(self, executor: IExecutor) -> dict:
        start_time = time.time()
        executor()
        return {"ExecutionTime (s)": time.time() - start_time}


class MemoryProfileReporter(IMetricsReporter):

    def report(self, executor: IExecutor) -> dict:
        mem_usage = memory_usage(executor, max_usage=True, include_children=True)
        return {"MemoryUsed (MiB)": mem_usage}


class MetricsReporterDecorator(IExecutor):

    def __init__(self, executor: IExecutor, metrics_reporters: [IMetricsReporter], logger: logging.Logger):
        self.executor = executor
        self.metrics_reporters = metrics_reporters
        self.logger = logger

    def __call__(self):
        result = {'task': self.get_name(), 'metrics': {}}
        for reporter in self.metrics_reporters:
            result['metrics'].update(reporter.report(self.executor))

        self.logger.info(json.dumps(result))

    def get_name(self) -> str:
        return self.executor.get_name()