# Created by saxenap (author: Praveen Saxena, email: saxep01@gmail.com) at 6/13/22
from dataclasses import dataclass
from datetime import datetime


class IAlgorithmName:
    def get_algorithm_name(self) -> str:
        raise NotImplementedError

    def create_new_cluster_name_for(self, clcluster_name: str) -> str:
        raise NotImplementedError


class IAlgorithmInfo:
    def get_name(self) -> str:
        raise NotImplementedError

    def get_id(self) -> int:
        raise NotImplementedError

    def get_create_datetime(self) -> datetime:
        raise NotImplementedError

    def get_last_updated(self) -> datetime:
        raise NotImplementedError

    def get_meta_json(self) -> str:
        raise NotImplementedError

    def get_comment(self) -> str:
        raise NotImplementedError

    def get_clusters(self) -> []:
        raise NotImplementedError


class Algorithm:
    def __init__(self, alg_info: IAlgorithmInfo, alg_name: IAlgorithmName, clusters: []):
        self.alg_info = alg_info
        self.alg_name = alg_name
        self.clusters = clusters

    def get_name(self) -> str:
        return self.alg_info.get_name()

    def get_clusters(self) -> []:
        return self.alg_info.get_clusters()

    def attach_cluster_for_span(self, ):


class IAlgorithmRepository:
    def get_clusters_for(self, algorithm_name: str) -> Algorithm:
        raise NotImplementedError

########################################################################################################################

class SpanTypes:
    BySemester: str = 'by_semester'
    ByDay: str = 'by_day'
    ByWeek: str = 'by_week'
    ByMonth: str = 'by_month'
    ByYear: str = 'by_year'


class IClusterSpan:
    def get_id(self) -> int:
        raise NotImplementedError

    def get_spans_from(self) -> datetime:
        raise NotImplementedError

    def get_spans_to(self) -> datetime:
        raise NotImplementedError

    def get_type(self) -> str:
        raise NotImplementedError


########################################################################################################################

class IClusterName:
    def get(self) -> str:
        raise NotImplementedError

    def __str__(self) -> str:
        raise NotImplementedError


class IClusterInfo:
    def get_span(self) -> IClusterSpan:
        raise NotImplementedError

    def get_algorithm_info(self) -> IAlgorithmInfo:
        raise NotImplementedError

    def get_name(self) -> IClusterName:
        raise NotImplementedError

    def get_id(self) -> int:
        raise NotImplementedError

    def get_create_datetime(self) -> datetime:
        raise NotImplementedError

    def get_last_updated(self) -> datetime:
        raise NotImplementedError

    def get_meta_json(self) -> str:
        raise NotImplementedError

    def get_comment(self) -> str:
        raise NotImplementedError


class Cluster:
    def __init__(self, cluster_info: IClusterInfo):
        self.cluster_info = cluster_info

    def get_algorithm(self) -> Algorithm:
        return Algorithm(self.cluster_info.get_algorithm_info())

########################################################################################################################





########################################################################################################################

class ClusterGroup:
    def __init__(self, algorithm: Algorithm, span: IClusterSpan):
        self.algorithm = algorithm
        self.span = span


    def attach_cluster(self, cluster_name: str) -> None:
        self.clusters.append = cluster