"""App module"""
import logging
import sys

import aiohttp


loggers = dict()

def setup_custom_logger(name) -> logging.Logger:
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


def init_client_session() -> aiohttp.ClientSession:
    """Create ClientSession with headers"""
    return aiohttp.ClientSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
        }
    )
