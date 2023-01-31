import logging
import importlib
import config

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

#convention to call/write functions
RUN_MODULE = config.RUN_MODULE
RUN_METHOD = config.RUN_METHOD

IO_MODULE = config.IO_MODULE
IO_METHOD = config.IO_METHOD


def read_job_output(job_name, id):

    module = importlib.import_module(IO_MODULE.format(job_name))
    function = getattr(module, IO_METHOD)
    return function(id)