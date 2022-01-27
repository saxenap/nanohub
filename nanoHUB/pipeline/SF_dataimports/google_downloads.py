from nanoHUB.logger import logger
import os
import io
import shutil
from pathlib import Path
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload


class LocalFolderConfiguration:
    def __init__(
            self,
            import_dir: Path,
            folder_name: str,
            to_import_folder_name: str,
            failures_folder_name: str,
            success_folder_name: str,
            log: logger
    ):
        self.import_dir = import_dir
        self.folder_name = folder_name
        self.to_import_folder_name = to_import_folder_name
        self.failures_folder_name = failures_folder_name
        self.success_folder_name = success_folder_name
        self.log = log
        self.configure()

    def get_import_dir_path(self):
        return self.import_dir_path

    def get_to_import_dir_path(self):
        return self.to_import_dir_path

    def get_failures_import_dir_path(self):
        return self.failures_import_dir_path

    def get_success_dir_path(self):
        return self.success_dir_path

    def configure(self):
        self.import_dir_path = Path.joinpath(self.import_dir, self.folder_name)
        self.import_dir_path.mkdir(parents=True, exist_ok=True)

        self.to_import_dir_path = Path.joinpath(self.import_dir_path, self.to_import_folder_name)
        self.to_import_dir_path.mkdir(parents=True, exist_ok=True)

        self.failures_import_dir_path = Path.joinpath(self.import_dir_path, self.failures_folder_name)
        self.failures_import_dir_path.mkdir(parents=True, exist_ok=True)

        self.success_dir_path = Path.joinpath(self.import_dir_path, self.success_folder_name)
        self.success_dir_path.mkdir(parents=True, exist_ok=True)

        for filename in os.listdir(self.to_import_dir_path):
            file_path = os.path.join(self.to_import_dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                self.log.debug("Removed existing file %s" % file_path)
            except Exception as e:
                self.log.error('Failed to delete %s. Reason: %s' % (file_path, e))


class GoogleDownloads:
    def __init__(self, service, config: LocalFolderConfiguration, log: logger):
        self.service = service
        self.config = config
        self.log = log

    def process(self) -> []:
        folder_id = self.get_folder_id()
        self.log.debug('Found folder: %s' % (folder_id))

        subfolder_id = self.get_subfolder_id()
        self.log.debug('Found subfolder: %s' % (subfolder_id))

        mimetypes = """
            mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' or
            mimeType = 'application/vnd.ms-excel' or
            mimeType = 'text/csv'
            """
        file_ids = []
        file_names = []
        page_token = None
        # q = "(" + mimetypes + ") and '" + folder.get('id') + "' in parents"
        while True:
            query = "(" + mimetypes + ") and '" + subfolder_id + "' in parents"
            response = self.service.files().list(
                q = query,
                spaces='drive',
                pageToken=page_token,
                fields="nextPageToken, files(id, name)"
            ).execute()

            self.log.debug(response)

            files = response.get('files', [])
            for file in files:
                self.log.info('Found file: %s (%s)' % (file.get('name'), file.get('id')))
                file_names.append(file['name'])
                file_ids.append(file['id'])
            page_token = response.get('nextPageToken', None)
            if page_token is None:
                break

        try:
            to_import_file_paths = []
            for temp_index,f_tbd_id in enumerate(file_ids):
                request = self.service.files().get_media(fileId=f_tbd_id) #,mimeType='text/csv') #if not .csv, then do .export()
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    self.log.debug("Downloading %s %d%%." % (file_names[temp_index], int(status.progress() * 100)))

                # The file has been downloaded into RAM, now save it in a file
                # https://stackoverflow.com/questions/60111361/how-to-download-a-file-from-google-drive-using-python-and-the-drive-api-v3
                fh.seek(0)

                download_filepath = Path(
                    self.config.get_to_import_dir_path(), file_names[temp_index]
                )
                with open(download_filepath, 'wb') as f:
                    shutil.copyfileobj(fh, f)

                to_import_file_paths.append(download_filepath)

                self.log.debug("Finished downloading files")
        except Exception as e:
            self.log.error("Error downloading file: " + str(e))
            raise

        return [to_import_file_paths, file_names, file_ids]

    def get_folder_id(self):
        response = self.service.files().list(
            q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + self.config.folder_name + "'",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        folder = response.get('files', [])[0]
        return folder.get('id')

    def get_subfolder_id(self):
        parent_folder_id = self.get_folder_id()
        subfolder_name = self.config.to_import_folder_name
        response = self.service.files().list(
            q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + subfolder_name + "'" + " and '" + parent_folder_id + "' in parents",
            spaces='drive',
            fields="files(id, name)"
        ).execute()
        folder = response.get('files', [])[0]
        return folder.get('id')

    def change_folder_for_file(self, file_id: str, old_folder_id: str, new_folder_id: str):
        return self.service.files().update(
            fileId=file_id,
            removeParents=old_folder_id,
            addParents=new_folder_id,
            fields='id, parents'
        ).execute()


class DefaultGoogleFactory:

    def __init__(self, application, log: logger):
        self.config = LocalFolderConfiguration(
            Path(os.getenv('APP_DIR') + '/.cache/'), 'Salesforce_Imports', 'To_Import', 'Import_Issues', 'Imported',
            log
        )
        self.downloader = GoogleDownloads(
            application.new_google_api_engine(),
            self.config,
            log
        )

    def get_folder_config(self):
        return self.config

    def get_downloader(self):
        return self.downloader