# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 5/23/22

class File:
    def get_id(self) -> str:
        raise NotImplementedError

    def get_possible_mimtypes(self) -> str:
        raise NotImplementedError

    def read(self, size=None, encoding: str ='utf-8') -> str:
        raise NotImplementedError

    def get_containing_folder_id(self) -> str:
        raise NotImplementedError


class Folder:
    def get_id(self) -> str:
        raise NotImplementedError

    def get_sub_folder(self, sub_folder_name: str) -> 'Folder':
        raise NotImplementedError

    def move_files(self, files: [], to_subfolder: 'Folder', force: bool = False):
        raise NotImplementedError

    def move_file(self, file: 'File', to_subfolder: 'Folder', force: bool = False):
        raise NotImplementedError

    def get_files(self, mimetypes: str) -> []:
        raise NotImplementedError

    def copy_files(self, files: [], force: bool = False) -> 'File':
        raise NotImplementedError

    def delete_files(self, files: []):
        raise NotImplementedError