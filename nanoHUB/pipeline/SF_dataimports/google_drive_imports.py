import os


from chardet import detect
from charset_normalizer import CharsetNormalizerMatches as CnM
from bs4 import BeautifulSoup
from bs4.dammit import EncodingDetector

def get_encoding_type(file_path):
    with open(file_path, 'rb') as f:
        rawdata = f.read()
    return detect(rawdata)


import_dir = os.getenv('APP_DIR') + '/.cache/SF_Imports'
list_files = [name for name in os.listdir(import_dir)] #if os.path.isfile(name)]

print("\n")
for file in list_files:
    file_path = import_dir + '/' + file
    from_chardet = get_encoding_type(file_path)
    from_normalizer = CnM.from_path(file_path).best().first().encoding

    f = open(file_path,"r")
    lines = f.readlines()
    from_beautifulsoup = EncodingDetector.find_declared_encoding(lines, is_html=False)

    print("Processing file: " + file + '---->')
    # if from_chardet is None:
    #     from_chardet = 'cp1252'
    # idf = pd.read_csv(file_path, encoding=from_codec['encoding'])
    print('From chardet ----> ' + from_chardet)
    print('From Normalizer ----> ' + from_normalizer)
    print('From BeautifulSoup ----> ' + from_beautifulsoup)
    print("\n")
    # print(idf)

# import pandas as pd
# import platform
# from copy import deepcopy
# from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
# from bs4 import UnicodeDammit
#
# from nanoHUB.application import Application
# from nanoHUB.logger import logger
# class GoogleDriveRepository:
#     def __init__(self, engine, logger):
#         self.engine = engine
#         self.logger = logger
#
#     def get_folder_id(self, folder_name: str):
#         response = self.engine.files().list(
#             q = "mimeType = 'application/vnd.google-apps.folder' and name = '" + folder_name + "'",
#             spaces='drive',
#             fields="files(id, name)"
#         ).execute()
#
#         folder = response.get('files', [])[0]
#         self.logger.info('Found folder: %s (%s)' % (folder.get('name'), folder.get('id')))
#         return folder.get('id')
#
#
# application = Application.get_instance()
#
# salesforce = application.new_salesforce_engine()
# db_s = salesforce
#
# FOLDER_NAME = 'Salesforce_Imports'
#
# google_repo = GoogleDriveRepository(
#     application.new_google_api_engine(),
#     logger('nanoHUB:google_imports')
# )
#
# folder_id = google_repo.get_folder_id(FOLDER_NAME)
# print(folder_id)
#
#
# import_dir = os.getenv('APP_DIR') + '/.cache/SF_Imports'
# with open(import_dir + '/Test2.csv', 'rb') as file:
#     content = file.read()
#
# suggestion = UnicodeDammit(content)
# print(suggestion.original_encoding)

