from dataclasses import dataclass, asdict
import json


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
