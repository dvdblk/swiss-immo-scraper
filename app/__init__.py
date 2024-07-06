"""App module"""
from typing import Any, Dict

import logging
import ssl
import sys
import time

import aiohttp


loggers = dict()


def setup_custom_logger(name) -> logging.Logger:
    """Create and return a custom logger"""
    if existing_log := loggers.get(name, None):
        return existing_log
    else:
        formatter = logging.Formatter(
            fmt="%(asctime)s.%(msecs)03d %(name)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(formatter)
        logger = logging.getLogger(name)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        loggers[name] = logger
        return logger


def init_client_session() -> aiohttp.ClientSession:
    """Create ClientSession with no-cache headers"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:127.0) Gecko/20100101 Firefox/127.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Priority": "u=1",
        "TE": "trailers"
    }

    async def add_nocache_headers(session, trace_config_ctx, params):
        params.headers.update({
            "X-No-Cache": str(time.time())
        })

    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(add_nocache_headers)

    ssl_context = ssl.create_default_context()
    ssl_context.set_ciphers("DEFAULT@SECLEVEL=1")
    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    ssl_context.maximum_version = ssl.TLSVersion.TLSv1_2
    tcp_connector = aiohttp.TCPConnector(
        ssl=ssl_context,
        use_dns_cache=False,
        ttl_dns_cache=300,
        limit=100
    )

    return aiohttp.ClientSession(headers=headers, trace_configs=[trace_config], connector=tcp_connector)