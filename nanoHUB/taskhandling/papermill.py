import Papermill
import subprocess
import sys

class PapermillHandler(ITaskHandler):
    def __init__(self, handler: ITaskHandler, papermill: Papermill):
        self.papermill = papermill
        self.handler = handler

    def execute(self, task: ITaskParameters) -> None:
        command = subprocess.run([papermill, task.get_file_path(), ], capture_output=True)
        sys.stdout.buffer.write(command.stdout)
        sys.stderr.buffer.write(command.stderr)
        sys.exit(command.returncode)
