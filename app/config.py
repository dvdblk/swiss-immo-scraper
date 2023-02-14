from typing import List, Optional

from pydantic import AnyHttpUrl, BaseSettings


class Config(BaseSettings):
    # Discord Webhook URL
    discord_webhook: AnyHttpUrl

    # Google Maps API key
    google_maps_api_key: Optional[str]
    # Used to compute the distance from the
    # apartment to the destination address
    google_maps_destination: Optional[str]

    # Sentry DSN for monitoring potential exceptions
    sentry_dsn: Optional[AnyHttpUrl]

    # List of Immo URLs that will be scraped.
    # You can use multiple URLs per one Immo website.
    scrape_urls: List[AnyHttpUrl]

    # Time delta between individual scrapes in seconds
    scraping_interval: int = 120
