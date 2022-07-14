from dataclasses import dataclass, asdict
import pandas as pd
import json
from dataclasses import dataclass, field
from nanoHUB.clustering.core_quick_cluster_detection.core_cost_cluster_analysis import  get_scratch_dir, core_cost_cluster_analysis
from nanoHUB.clustering.core_classroom_detection.core_classroom_analysis import core_classroom_analysis
from nanoHUB.clustering.save_clusters_to_geddes import save_clusters_to_geddes
from nanoHUB.clustering.preprocessing.gather_data import gather_data
import os
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
    core_cost_cluster_analysis: str = 'core_cost_cluster_analysis'

    def __str__(self) -> str:
        return json.dumps(asdict(self))

    def return_algorithms(self):
        alg_list = []
        for func in self.__dataclass_fields__:
            algorithm = getattr(self, func)
            if algorithm not in alg_list:
                print('Will run: ' + algorithm + ' algorithm.')
                alg_list.append(algorithm)

        return alg_list


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
        command.class_probe_range = [command.start_date, command.end_date]
        command.data_probe_range = [datetime.strptime(x, '%Y-%m-%d') for x in command.class_probe_range]

        if  not command.task or not hasattr(self._map, command.task):
            raise Exception(
                "Invalid Algorithm/Task %s. A valid task must be assigned. Valid algorithms/tasks are: %s" % (command.task, self._map)
            )

        if not os.path.exists(command.scratch_dir):
            os.mkdir(command.scratch_dir)

        if not os.path.exists(get_scratch_dir(command)):
            logging.info('Creating new scratch directory: ' + get_scratch_dir(command))
            os.mkdir(get_scratch_dir(command))

        if command.use_old_data == False:
            logging.info('Gathering data .....')
            gather_data(command)
        else:
            self.logger.info('Option "--user_old_data" enabled. Using data from previous run')

        if command.gather_data_only:
            self.logger.info("Only gathering data required => Returning empty dataframe.")
            return pd.DataFrame()

        func = getattr(self._map, command.task)
        try:
            self.logger.info("Running %s now." % func)
            return globals()[func](command)
        except KeyError as e:
            self.logger.error(
                "%s not found in the list of imported global modules. Make sure %s is imported." % (func, func)
            )


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

        df_dict = self.handler.handle(command)
        if command.save_to_geddes == True:
            command.object_path = 'clusters/' + command.task + '/by_semester'
            save_clusters_to_geddes(df_dict, command)
        return df_dict


class LocalDriveSaver(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df_dict = self.handler.handle(command)
        if not os.path.exists(command.output_dir):
            os.mkdir(command.output_dir)

        if command.no_save_output == True:
            self.logger.info("Skipping saving output locally.")
        else:
            path = command.output_dir + '/' + command.task + '/by_semester/' + command.class_probe_range[0] + '_' + command.class_probe_range[1]
            self.logger.info("Saving output locally at %s" % path)

            for key in df_dict:
                path = command.output_dir + '/' + command.task + '/by_semester/' + command.class_probe_range[0] + '_' + \
                       command.class_probe_range[1] + '/' + key + '.csv'
                df_dict[key].to_csv(path)

        return df_dict


class DatabaseSaver(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df_dict = self.handler.handle(command)
        return df_dict


class DisplayDf(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df_dict = self.handler.handle(command)
        if command.display_output:
            print(df_dict)
        return df_dict


class DataframeLogger(IExecuteAlgorithm):
    def __init__(self, handler: IExecuteAlgorithm, logger: logging.Logger):
        self.handler = handler
        self.logger = logger

    def handle(self, command) -> pd.DataFrame:
        df_dict = self.handler.handle(command)
        self.logger.debug(df_dict)
        return df_dict
