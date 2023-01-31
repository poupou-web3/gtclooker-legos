from lib.utils.commons import read_yaml
import argparse
import logging
import importlib
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


RUN_MODULE = config.RUN_MODULE
RUN_METHOD = config.RUN_METHOD
JOB_CONFIG = config.JOB_CONFIG


if __name__ == "__main__":
    """
    job entry point
    """

    parser = argparse.ArgumentParser(description='jobs')
    parser.add_argument('-n', '--name', help='job name. check job.yaml')

    args = parser.parse_args()
    job_name = args.name

    logger.info(f"starting job {args.name}")


    job_config = [c for c in read_yaml(JOB_CONFIG)['legos'] if c['name'] ==job_name][0]

    module = importlib.import_module(RUN_MODULE.format(job_name))
    function = getattr(module, RUN_METHOD)
    function(job_config['id'], job_config.get('inputs',[]), job_config.get('params',{}))