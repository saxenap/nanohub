# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 5/23/22

import os
import re
import shutil
from nanoHUB.domain.interfaces import File, Folder


class LocalFile(File):
    def __init__(self, file_path: str):
        self._filepath = file_path

    def read(self, size=None, encoding: str ='utf-8') -> str:
        with open(self._filepath) as _file:
            if size:
                data = _file.read(size)
            else:
                data = _file.read()
        return data


class LocalFolder(Folder):
    def __init__(self, file_path: str):
        self._filepath = file_path

    def move(self, dest, force: bool = False) -> 'File':
        if force == False and os.path.isfile(dest):
            raise IOError('Destination file already exists')
        shutil.move(self._filepath, dest)
        return self.__class__(dest)

    def copy(self, dest, force: bool = False) -> 'File':
        if force == False and os.path.isfile(dest):
            raise IOError('Destination file already exists')
        shutil.copy(self._filepath, dest)
        return self.__class__(dest)

    def delete(self):
        os.remove(self._filepath)

