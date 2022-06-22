from dataclasses import dataclass, asdict
import pandas as pd
import json
from dataclasses import dataclass, field
from core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from core_quick_cluster_detection.core_cost_cluster_analysis import core_cost_cluster_analysis
from save_clusters_to_geddes import save_clusters_to_geddes
from preprocessing.gather_data import gather_data
from pprint import pprint, pformat
from datetime import datetime, date
import logging


class IValidator:
    def validate(self, command) -> None:
        raise NotImplementedError()


class DateValidator(IValidator):
    def validate(self, command) -> None:
        if not command.class_probe_range:
            command.class_probe_range = command.start_date + ":" + command.end_date

        start_check = datetime.strptime(command.start_date, '%Y-%m-%d')
        end_check = datetime.strptime(command.end_date, '%Y-%m-%d')

        if not start_check < end_check:
            raise Exception("start_date before end_date")


@dataclass
class AlgorithmsMap:
    xufeng: str = 'core_classroom_analysis'
    classroom_detection: str = 'core_classroom_analysis'
    core_classroom_analysis: str = 'core_classroom_analysis'

    mike: str = 'core_cost_cluster_analysis'
    cost_cluster_analysis: str = 'core_cost_cluster_analysis'
    core_cost_cluster_analysis: str = 'cost_cluster_analysis'

    def __str__(self) -> str:
        return json.dumps(asdict(self))


class IExecuteAlgorithm:
    def handle(self, command) -> pd.DataFrame:
        raise NotImplementedError()


class ValidationHandler(IExecuteAlgorithm):
    def __init__(self, validators: [], handler: IExecuteAlgorithm, logger: logging.Logger):
        self.validators = validators
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        for validator in self.validators:
            validator.validate(command)

        return self.handler.handle(command)


class AlgorithmHandler(IExecuteAlgorithm):
    def __init__(self, _map: AlgorithmsMap, logger: logging.Logger):
        self._map = _map
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        if command.use_old_data == False:
            logging.info('Gathering data .....')
            gather_data(command)
        else:
            self.logger.info('Option "--user_old_data" enabled. Using data from previous run')

        if command.gather_data_only:
            self.logger.info("Only gathering data required => Returning empty dataframe ...")
            return pd.DataFrame()

        if  not command.task or not hasattr(self._map, command.task):
            raise Exception(
                "Invalid Algorithm/Task %s. A valid task must be assigned. Valid algorithms/tasks are: %s" % (command.task, self._map)
            )

        func = getattr(self._map, command.task)
        return func(command)


class GeddesSaver(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        if command.save_to_geddes == True:
            if command.bucket_name is None or command.bucket_name == '':
                raise ValueError("A bucket name is necessary in order to save results to Geddes")
            if command.object_path is None or command.object_path == '':
                raise ValueError("A object path is necessary in order to save results to Geddes")
        else:
            self.logger.info("Skipping saving output in Geddes ...")

        df = self.handler.handle(command)
        if command.save_to_geddes == True:
            command.object_path = 'clusters/${' + command.task + '}/by_semester'
            save_clusters_to_geddes(df, command)
        return df


class LocalDriveSaver(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df = self.handler.handle(command)
        if command.no_save_output == True:
            self.logger.info("Skipping saving output locally...")

        return df


class DatabaseSaver(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df = self.handler.handle(command)
        return df


class DisplayDf(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df = self.handler.handle(command)
        print(df)
        return df


class DataframeLogger(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df = self.handler.handle(command)
        self.logger.info(df)
        return df
