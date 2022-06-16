import datetime, time, argparse
from nanoHUB.application import Application
from nanoHUB.configuration import ClusteringConfiguration
from nanoHUB.clustering.infra import create_mike_xufeng_overlap_repo
from nanoHUB.dataaccess.lake import UnderscoredDateParser
import logging


def overlap_by_semester():
    parser = argparse.ArgumentParser(
        description='Create and upload cluster overlaps to Geddes'
    )

    # task options
    parser.add_argument('--class_probe_range',
                        help='classroom detection: date range of the class to be analyzed. For example, 2018-1-1_2018-5-1',
                        action='store', default='latest')  # 'c')

    parser.add_argument('--log_level', help='logging level (INFO, DEBUG etc)',
                        action='store', default='INFO')

    inparams = parser.parse_args()

    numeric_level = getattr(logging, inparams.log_level.upper(), 10)
    logging.basicConfig(level=numeric_level, format='%(message)s')

    repo = create_mike_xufeng_overlap_repo(
        Application.get_instance(), ClusteringConfiguration().bucket_name_processed
    )

    date_parser = UnderscoredDateParser()
    from_date, to_date = date_parser.parse_time_probe(inparams.class_probe_range)
    repo.save_for(from_date, to_date)


if __name__ == '__main__':
    start = time.time()
    overlap_by_semester()
    end = time.time()
    print("Time:", end - start)

