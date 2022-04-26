"""App module"""
import logging
import sys

loggers = dict()

def setup_custom_logger(name):
    """Create and return a custom logger"""
    if existing_log := loggers.get(name, None):
        return existing_log
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d %(name)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        loggers[name] = logger
        return logger
