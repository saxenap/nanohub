import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import papermill

import logging
from pathlib import Path
import subprocess


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
        output_file_path = self.outfile_path + '/' + Path(self.notebook_path).name
        papermill.execute_notebook(
            self.notebook_path,
            output_file_path,
            log_output=True,
            report_mode=True
        )
        self.logger.info('Saved output file - %s' % output_file_path)

    def get_name(self) -> str:
        return 'JupyterExecutor (file: %s)'% __file__


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
        return 'PythonFileExecutor (file: %s)'% __file__


class RFileExecutor(IExecutor):

    def __init__(self, r_executable_path: str, file_path: str, outfile_path: str, logger: logging.Logger):
        self.file_path = file_path
        self.r_executable_path = r_executable_path
        self.outfile_path = outfile_path
        self.logger = logger

    def __call__(self):
        subprocess.call([self.r_executable_path, "--vanilla", self.file_path])

    def get_name(self) -> str:
        return 'RFileExecutor (file: %s)'% __file__

'''
##################################################################################################

Decorating Executors

##################################################################################################
'''

class LoggingExecutorDecorator(IExecutor):

    def __init__(self, executor: IExecutor, file_path: str, logger: logging.Logger):
        self.executor = executor
        self.file_path = file_path
        self.logger = logger
        # self.test = 0

    def __call__(self):
        self.executor()
        # self.test += 1
        # if self.test == 1:
        #     raise RuntimeError
        self.logger.info("%s executed file/task %s." % (self.executor.get_name(), self.file_path))

    def get_name(self) -> str:
        return 'LoggingExecutorDecorator (file: %s)'% __file__


class RetryingExecutorDecorator(IExecutor):

    def __init__(self, executor: IExecutor, retries_max_count: int, logger: logging.Logger):
        self.executor = executor
        self.retries_max_count = retries_max_count
        self.retries_current_count = 0
        self.logger = logger

    def __call__(self):
        for i in range(0, self.retries_max_count):
            try:
                self.retries_current_count += 1
                self.logger.info("Executing task - number of tries left: %d." % (self.retries_max_count - self.retries_current_count))
                self.executor()
                return
            except Exception as excep:
                self.logger.info("Task failed with exception %s." % excep)
                continue


    def get_name(self) -> str:
        return 'RetryingExecutorDecorator (file: %s)'% __file__


import time

class TimeProfilingDecorator(IExecutor):

    def __init__(self, executor: IExecutor, logger: logging.Logger):
        self.executor = executor
        self.logger = logger

    def __call__(self):
        start_time = time.time()
        self.executor()
        stop_time = time.time() - start_time
        self.logger.info("Time Taken - %ss" % stop_time)


from memory_profiler import memory_usage

class MemoryProfilingDecorator(IExecutor):

    def __init__(self, executor: IExecutor, logger: logging.Logger):
        self.executor = executor
        self.logger = logger

    def __call__(self):
        mem_usage = memory_usage((self.executor), max_usage=True, include_children=True)
        self.logger.info("Memory Used - %.2fMB" % mem_usage)
