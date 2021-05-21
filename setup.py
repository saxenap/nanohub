
from setuptools import setup, find_packages

setup(
    name         = 'nanoHUB',
    version      = '1.0',
    packages=find_packages(exclude=('tests')),
)