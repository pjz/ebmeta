import sys
import logging


def stderr_handler():
    handler = logging.StreamHandler(stream=sys.stderr)
    formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)
    return handler


logger = logging.getLogger(__name__)
logger.addHandler(stderr_handler())

