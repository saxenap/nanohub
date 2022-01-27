from chardet import detect
from charset_normalizer import CharsetNormalizerMatches as CnM
import pandas as pd
from nanoHUB.logger import logger
from pathlib import Path


class MappingConfiguration:
    def __init__(
            self,
            possible_encodings: list,
            possible_separators: list,
            possible_engines: list
    ):
        self.possible_encodings = possible_encodings
        self.possible_separators = possible_separators
        self.possible_engines = possible_engines

    def get_possible_encodings(self) -> []:
        return self.possible_encodings

    def get_possible_separators(self) -> []:
        return self.possible_separators

    def get_possible_engines(self) -> []:
        return self.possible_engines


class FileToDFMapper:
    def __init__(self, config: MappingConfiguration, logger: logger):
        self.logger = logger
        self.config = config

    def get_encoding_type(self, file_path: Path):
        from_normalizer = CnM.from_path(
            str(file_path)
        ).best().first().encoding

        return from_normalizer

    def read_file_to_df(self, file_path: Path) -> pd.DataFrame:
        possible_encodings = [
            'utf-8', 'cp1252', 'utf-16', 'cp1254', 'cp775', 'utf-8-sig', 'iso-8859-1', 'unicode_escape', 'gbk','latin1'
        ]
        possible_separators = [',', '\t']
        possible_engines = ['c', 'python']

        for encoding in possible_encodings:
            for sep in possible_separators:
                for engine in possible_engines:
                    try:
                        idf = pd.read_csv(file_path, encoding=encoding, sep=sep, engine=engine)
                        self.logger.info("File with Encoding: %s and Separator: %s processed using engine %s" % (encoding, sep, engine))
                        return idf
                    except Exception as e:
                        self.logger.debug("Decoding failed with %s, %s, %s" % (encoding, sep, engine))
                        pass
        self.logger.info("Either the file (%s) is empty or unable to decode." % file_path)
        return pd.DataFrame()


class DefaultMapperFactory:
    def __init__(self, logger: logger):
        self.logger = logger

    def create_new(self) -> FileToDFMapper:
        config = MappingConfiguration(
            [
                'utf-8', 'cp1252', 'utf-16', 'cp1254', 'cp775', 'utf-8-sig', 'iso-8859-1', 'unicode_escape', 'gbk','latin1'
            ],
            [',', '\t'],
            ['c', 'python']
        )

        return FileToDFMapper(config, self.logger)


class FileType:
    def __init__(self, logger: logger):
        self.logger = logger

    def process(self, file_path: Path) -> pd.DataFrame:
        raise NotImplementedError


class ExcelFile(FileType):
    def process(self, file_path: Path):
        try:
            xl = pd.ExcelFile(file_path)
            self.logger.debug("sheet names: " + xl.sheet_names)# see all sheet names
            sheet_names = xl.parse(xl.sheet_names) #this already performs an import
            idf = pd.read_excel(file_path,sheet_name=xl.sheet_names[0],header=0)#,skiprows=1)
        except:
            self.logger.error('error bad lines, csv/xls/xlsx import failed')
            raise TypeError


class EmptyOrEncodingIssue(TypeError):
    """Either the file is empty or was unable to be read properly."""


def map_file(file_path: Path, log: logger) -> pd.DataFrame:
    factory = DefaultMapperFactory(log)

    f_type = file_path.suffix
    log.info("File type %s" % f_type)

    mapper = factory.create_new()
    log.info("Encoding is of type: %s" % mapper.get_encoding_type(file_path))

    idf = pd.DataFrame
    if f_type == '.csv':
        log.debug("csv file type identified")
        idf = mapper.read_file_to_df(file_path)

    elif f_type == '.xlsx' or f_type == '.xls':
        idf = ExcelFile(log).process(file_path)

    if idf.empty:
        raise EmptyOrEncodingIssue

    return idf