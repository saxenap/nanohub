import logging

from nanoHUB.settings import Settings
from nanoHUB.logger import logger
from nanoHUB.pipeline.application import Application
import os, sys, argparse

parser = argparse.ArgumentParser(description='Execute task.')
subparsers = parser.add_subparsers()
arg1 = subparsers.add_parser('task')
arg1.add_argument("--file-path")
arg1.add_argument('--log-level', '-log', default='INFO')


def main() -> None:

    db_connection = container.database.db_connection_factory()
    executor = container.get_executor()
    executor()

    logger().info("Main called")


if __name__ == '__main__':

    args = parser.parse_args()
    container = Application.get_instance()
    Application.set_filepath(vars(args)['file_path'])
    logger().setLevel(logging.getLevelName(vars(args)['log_level']))

    main()
