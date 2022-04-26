from urllib.parse import (
    urlsplit,
    urlunsplit,
    urlencode
)
from math import ceil

from aiohttp import ClientSession


async def compute_distance(
    session: ClientSession, gmaps_api_key: str, origin_address: str,
    destination: str = "Rämistrasse, Zürich, Switzerland"
) -> tuple[str, str]:
    """Use Google Maps API to compute the distance (minutes and kms)
    from a given address to the destination

    Returns:
        distance (str): distance in km as string with unit 'km' or None
        minutes (str): distance in minutes as string with unit 'mins' or None
    """
    url = "https://maps.googleapis.com/maps/api/distancematrix/json"
    scheme, netloc, path, _, fragment = urlsplit(url)
    url = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=Boston%2CMA%7CCharlestown%2CMA&destinations=Lexington%2CMA%7CConcord%2CMA&departure_time=now&key=YOUR_API_KEY"

    url_params = {
        "origins": origin_address,
        "destinations": destination,
        "key": gmaps_api_key
    }
    query_params = urlencode(url_params)

    request_url = urlunsplit((scheme, netloc, path, query_params, fragment))
    resp = await session.get(request_url)
    if resp.status == 200:
        resp_json = await resp.json()
        try:
            # Get distance in minutes and kilometers
            distance = resp_json["rows"][0]["elements"][0]["distance"]["text"]
            duration_value = resp_json["rows"][0]["elements"][0]["duration"]["value"]
            duration = ceil(duration_value / 60)

            return distance, f"{duration} min."
        except (KeyError, IndexError):
            pass

    return None, None
