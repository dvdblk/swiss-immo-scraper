from typing import List, Optional, Tuple

from pydantic import AnyHttpUrl, BaseSettings


class Config(BaseSettings):
    # Discord Webhook URL
    discord_webhook: AnyHttpUrl

    # Google Maps API key
    google_maps_api_key: Optional[str]
    # Used to compute the distance from the
    # apartment to the destination address
    google_maps_destination: Optional[str]

    # List of Immo URLs that will be scraped.
    # You can use multiple URLs per one Immo website.
    scrape_urls: List[AnyHttpUrl]

    # Preview mode, if true, the app will send the last
    # apartment / object found on the scraping URLs to the webhook
    preview_mode: Optional[bool] = False
