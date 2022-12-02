# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 5/23/22
import logging
import os
import io
import shutil
from nanoHUB.domain.interfaces import File, Folder
from dataclasses import dataclass
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
import tempfile


@dataclass
class FolderParams:
    folder_name: str
    folder_id: str


@dataclass
class FileParams:
    file_name: str
    file_id: str
    folder_id: str
    sub_folder_id: str
    possible_mimetypes: str


class FolderNotFound(FileNotFoundError):
    """
    Raised to signal that the folder does not exist.
    """

class GoogleFolder(Folder):
    def __init__(self, service, folder_name: str, folder_id: str, parent_folder_id: str, logger: logging.Logger):
        self.service = service
        self.folder_name = folder_name
        self.folder_id = folder_id
        self.parent_folder_id = parent_folder_id
        self.logger = logger

    @staticmethod
    def init_by_name(folder_name: str, service, logger) -> 'Folder':
        response = service.files().list(
            q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + folder_name + "'",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        folder = response.get('files', [])[0]
        return GoogleFolder(service, folder_name, folder.get('id'), '', logger)

    def get_id(self) -> str:
        return self.folder_id

    def get_sub_folder(self, sub_folder_name: str) -> 'Folder':
        parent_folder_id = self.get_id()
        response = self.service.files().list(
            q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + sub_folder_name + "'" + " and '" + parent_folder_id + "' in parents",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        try:
            print(parent_folder_id)
            folder = response.get('files', [])[0]
            return GoogleFolder(self.service, sub_folder_name, folder.get('id'), self.get_id(), self.logger)
        except IndexError as ie:
            logging.exception( ie )

            raise FolderNotFound("%s/%s - No such folder exists." % (self.folder_name, sub_folder_name))

    def move_files(self, files: [], to_subfolder: 'Folder', force: bool = False):
        for file in files:
            self.move_file(file, to_subfolder)

    def move_file(self, file: 'File', to_subfolder: 'Folder', force: bool = False):
        self.service.files().update(
            fileId = file.get_id(),
            removeParents = file.get_containing_folder_id(),
            addParents = to_subfolder.get_id(),
            fields='id, parents'
        ).execute()

    def get_files(self, mimetypes: str = """
            mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or
            mimeType = 'application/vnd.ms-excel' or
            mimeType = 'text/csv'
            """):
        files_result = []
        page_token = None
        if self.parent_folder_id == '':
            query = "(" + mimetypes + ")"
        else:
            query = "(" + mimetypes + ") and '" + self.folder_id + "' in parents"
        while True:
            response = self.service.files().list(
                q = query,
                spaces='drive',
                pageToken=page_token,
                fields="nextPageToken, files(id, name)"
            ).execute()
            files = response.get('files', [])
            for file in files:
                self.logger.info('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                files_result.append(GoogleFile(
                    self.service,
                    FileParams(file['name'], file['id'], self.get_id(), self.parent_folder_id, mimetypes),
                    self.logger
                ))
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break
        return files_result


class GoogleFile(File):
    def __init__(self, service, params: FileParams, logger: logging.Logger):
        self.service = service
        self.params = params
        self.logger = logger

    def get_id(self) -> str:
        return self.params.file_id

    def get_possible_mimtypes(self) -> str:
        return self.params.possible_mimetypes

    def read(self, size=None, encoding: str ='utf-8') -> str:
        request = self.service.files().get_media(fileId=self.params.file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        self.logger.info("Reading all files of mimetypes: %s" % self.params.possible_mimetypes)
        while done is False:
            status, done = downloader.next_chunk()
            self.logger.info("Downloading %s %d%%." % (self.params.file_name, int(status.progress() * 100)))
        fh.seek(0)
        temp_file = tempfile.NamedTemporaryFile()
        temp_filename = temp_file.name
        with open(temp_filename, 'wb') as f:
            shutil.copyfileobj(fh, f)
        return open(temp_filename,"r", encoding='utf8').read()

    def get_containing_folder_id(self) -> str:
        return self.params.folder_id

