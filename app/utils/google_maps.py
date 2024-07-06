from urllib.parse import (
    urlsplit,
    urlunsplit,
    urlencode
)
from math import ceil

import asyncio
from aiohttp import ClientSession


async def compute_distance(
    session: ClientSession, gmaps_api_key: str, origin_address: str,
    destination_address: str = "Rämistrasse, Zürich, Switzerland"
) -> tuple[str, str]:
    """Use Google Maps API to compute the distance (minutes and kms)
    from a given address to the destination

    Returns:
        distance (str): distance in km as string with unit 'km' or None
        minutes (str): distance in minutes as string with unit 'mins' or None
    """
    base_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    scheme, netloc, path, _, fragment = urlsplit(base_url)

    modes = ["driving", "transit", "bicycling"]

    results = {}

    async def fetch_distance(mode):
        url_params = {
            "origins": origin_address,
            "destinations": destination_address,
            "mode": mode,
            "key": gmaps_api_key
        }
        query_params = urlencode(url_params)
        request_url = urlunsplit((scheme, netloc, path, query_params, fragment))

        async with session.get(request_url) as resp:
            if resp.status == 200:
                resp_json = await resp.json()
                try:
                    element = resp_json["rows"][0]["elements"][0]
                    distance = element["distance"]["text"]
                    duration = element["duration"]["text"]
                    return mode, (distance, duration)
                except (KeyError, IndexError):
                    return mode, (None, None)
            else:
                return mode, (None, None)

    results = dict(await asyncio.gather(*(fetch_distance(mode) for mode in modes)))
    return results
