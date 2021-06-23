
from setuptools import setup, find_packages

setup(
    name         = 'nanoHUB',
    version      = '1.0',
    install_requires=['setuptools-git'],
    include_package_data=True,
    packages=find_packages(),

    entry_points={
        "console_scripts": [
            "nanohub=nanoHUB.__main__:app",
            "nanoHUB=nanoHUB.__main__:app"
        ]
    }
)