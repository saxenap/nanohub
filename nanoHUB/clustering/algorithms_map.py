from dataclasses import dataclass, asdict
import pandas as pd
import json
import logging
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from core_quick_cluster_detection.core_cost_cluster_analysis import core_cost_cluster_analysis
from save_clusters_to_geddes import save_clusters_to_geddes
from preprocessing.gather_data import gather_data
from pprint import pprint, pformat

class IPreExecutor:
    def preexecute(flags) -> None:
        raise NotImplementedError()


class DateMapper(IPreExecutor):
    def preexecute(flags) -> None:
        if not self.class_probe_range:
            self.class_probe_range = self.start_date + ":" + self.end_date

        start_check = datetime.strptime(flags.start_date, '%Y-%m-%d')
        end_check = datetime.strptime(flags.end_date, '%Y-%m-%d')

        if not start_check < end_check:
            raise Exception("start_date before end_date")


@dataclass
class AlgorithmsMap:
    xufeng: str = 'core_classroom_analysis'
    classroom_detection: str = 'core_classroom_analysis'
    core_classroom_analysis: str = 'core_classroom_analysis'

    mike: str = 'core_cost_cluster_analysis'
    cost_cluster_analysis: str = 'core_cost_cluster_analysis'
    cost_cluster_analysis: str = 'cost_cluster_analysis'


    def __str__(self) -> str:
        return json.dumps(asdict(self))

class DataLoader(IPreExecutor):
    def execute(flags) -> None:
        if flags.use_old_data == False:
            logging.info('Gathering data .....')
            gather_data(flags)
        else:
            logging.info('Option "--user_old_data" enabled. Using data from previous run')

        logging.debug(pformat(vars(flags)))

class IAlgorithmExecutor:
    def execute(flags) -> pd.DataFrame:
        raise NotImplementedError()

class AlgorithmExecutor(IAlgorithmExecutor):
    def __init__(preexecutors: [], _map: AlgorithmsMap):
        self.preexecutors = preexecuttors
        self._map = _map

    def execute(flags) -> pd.DataFrame:
        for preexecutor in self.preexecutors:
            execute(flags)

            self.data_loader(flags)
            if flags.gather_data_only:
                return
            if not hasattr(_map, flags.task)
                raise ValueError("A task must be assigned.")
            func = getattr(_map, flags.task)
            return func(flags)

class GeddesSaver(IAlgorithmExecutor):
    def __init__(executor: IAlgorithmExecutor):
        self.executor = executor

    def execute(flags) -> pd.DataFrame:
        if flags.save_to_geddes == True:
            if flags.bucket_name is None or flags.bucket_name == '':
                raise ValueError("A bucket name is necessary in order to save results to Geddes")
            if flags.object_path is None or flags.object_path == '':
                raise ValueError("A object path is necessary in order to save results to Geddes")
        else:
            logging.info("Skipping saving output in Geddes ...")

        df = self.executor.execute(flags)
        if flags.save_to_geddes == True:
            save_clusters_to_geddes(df, flags)
        return df

class LocalDriveSaver(IAlgorithmExecutor):
    def __init__(executor: IAlgorithmExecutor):
        self.executor = executor

    def execute(flags) -> pd.DataFrame:
        df = self.executor.execute()
        if flags.no_save_output == True:
            logging.info("Skipping saving output locally...")

        return df

class DatabaseSaver(IAlgorithmExecutor):
    def __init__(executor: IAlgorithmExecutor):
        self.executor = executor

    def execute(flags) -> pd.DataFrame:
        df = self.executor.execute(flags)
        return df

class DisplayDf(IAlgorithmExecutor):
    def __init__(executor: IAlgorithmExecutor):
        self.executor = executor

    def execute(flags) -> pd.DataFrame:
        df = self.executor.execute(flags)
        print(df)
        return df

class DataframeLogger(IAlgorithmExecutor):
    def __init__(executor: IAlgorithmExecutor):
        self.executor = executor

    def execute(flags) -> pd.DataFrame:
        df = self.executor.execute(flags)
        self.logger.info(df)
        return df