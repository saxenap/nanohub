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


def main(args) -> None:

    application = Application.get_instance()
    application.execute(vars(args)['file_path'])
    logger().info("Main called")


if __name__ == '__main__':

    args = parser.parse_args()
    logger().setLevel(logging.getLevelName(vars(args)['log_level']))
    main(args)
