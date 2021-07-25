import logging
import re
from nanoHUB.dataaccess.common import QueryParams
from pandas.core.frame import DataFrame
from pathlib import Path
import pandas


class IFiles:
    def exists(self, dirpath: Path) -> bool:
        raise NotImplemented

    def read_all(self, dirpath: Path) -> DataFrame:
        raise NotImplemented

    def save(self, df: DataFrame, outdir: Path, outfile: str):
        raise NotImplemented


class CsvFiles(IFiles):

    def exists(self, dirpath: Path) -> bool:
        for file in dirpath.glob('*.csv'):
            return True
        return False

    def read_all(self, dirpath: Path) -> DataFrame:
        return pandas.concat(
            pandas.read_csv(csv_file)
            for csv_file in dirpath.glob('*.csv')
        )

    def save(self, df: DataFrame, outdir: Path, outfile: str):
        outfile = outfile + '.csv'
        df.to_csv(outdir / outfile)


class AbstractCompressableFiles(IFiles):
    def __init__(self, compress: bool = True):
        self.compress = compress


class ParquetFiles(AbstractCompressableFiles):

    def get_file_extension(self):
        if self.compress is True:
            return 'parquet.gzip'
        return 'parquet'

    def exists(self, dirpath: Path) -> bool:
        for file in dirpath.glob('*.'+ self.get_file_extension()):
            return True
        return False

    def read_last(self, dirpath: Path) -> DataFrame:
        extension = self.get_file_extension()
        max = -1
        for file in dirpath.glob('*.' + extension):
            num = int(re.search('(\d*)', file.name).group(1))
            max = num if num > max else max
        return pandas.read_parquet(Path(dirpath, str(max)).with_suffix(extension))

    def read_all(self, dirpath: Path) -> DataFrame:
        extension = self.get_file_extension()
        return pandas.concat(
            pandas.read_parquet(parquet_file)
            for parquet_file in dirpath.glob('*.' + extension)
        )

    def save(self, df: DataFrame, outdir: Path, outfile: str):
        outfile = outfile + '.' + self.get_file_extension()
        if self.compress:
            df.to_parquet(outdir / outfile, compression='gzip')
        else:
            df.to_parquet(outdir / outfile)


class CachedDataLoader:
    def __init__(self, files: IFiles, path: str, logger: logging.Logger):
        self.files = files
        self.path = path
        self.logger = logger
        self.count = {}

    def exists(self, params: QueryParams) -> bool:
        outdir = Path(self.path + '/' + params.db_name + '/' + params.table_name + '/')
        if outdir.is_dir():
            has_next = next(outdir.iterdir(), None)
            if has_next is not None:
                return self.files.exists(outdir)
        self.logger.debug('Data for %s.%s not found in cache' % (params.db_name, params.table_name))
        print('Data for %s.%s not found in cache' % (params.db_name, params.table_name))
        return False

    def get_all(self, params: QueryParams) -> DataFrame:
        datadir = Path(self.path + '/' + params.db_name + '/' + params.table_name + '/')

        self.logger.debug('Reading data for %s.%s from %s' % (params.db_name, params.table_name, datadir))
        df = self.files.read_all(datadir)
        df = df.sort_values(params.index_key)
        return df

    def save(self, df: DataFrame, params: QueryParams, incremental: bool = False):

        outdir = Path(self.path + '/' + params.db_name + '/' + params.table_name + '/')

        if not params.db_name in self.count:
            self.count[params.db_name] = {}
            self.logger.debug('Saving data for database %s' % params.db_name)
            print('Saving data for database %s' % params.db_name)

        if not params.table_name in self.count[params.db_name]:
            self.count[params.db_name][params.table_name] = 0
            outdir.mkdir(parents=True, exist_ok=True)
            print('Saving data for table %s.%s' % (params.db_name, params.table_name))
            self.logger.debug('Saving data for table %s.%s' % (params.db_name, params.table_name))

        self.count[params.db_name][params.table_name] += 1
        outfile = str(self.count[params.db_name][params.table_name])
        self.logger.debug('Saving data in %s/%s with %d rows of data' % (outdir, outfile, len(df.index)))
        print('Saving data in %s/%s with %d rows of data' % (outdir, outfile, len(df.index)))
        self.files.save(df, outdir, outfile)
