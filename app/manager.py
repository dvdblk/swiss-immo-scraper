"""Manager for scraping individual immo websites and sending discord messages"""
import asyncio
import os
from urllib.parse import urlparse

from aiohttp import ClientSession
from discord import (
    Webhook,
    AsyncWebhookAdapter
)

from app import setup_custom_logger
from app.scraper import Scraper
from app.immo.model import ImmoData
from app.discord_utils import send_discord_listing_embed
from app.google_maps import compute_distance


class ImmoManager:
    """do stuff"""
    # Time delta between individual scrapes
    N_SECONDS_SLEEP = 120

    def __init__(
        self, web_data: dict, session: ClientSession, use_google_maps: bool
    ):
        # Env vars
        discord_webhook_url = os.environ["DISCORD_WEBHOOK"]
        self.google_maps_api_key = os.environ["GOOGLE_MAPS_API_KEY"] if use_google_maps else None

        # Data
        self.web_data = web_data
        self.parsed_url = urlparse(web_data["url"])
        self.listings = []

        # Instances
        self.logger = setup_custom_logger(".".join([__name__, self.parsed_url.hostname]))
        self.scraper = Scraper(parsed_url=self.parsed_url, session=session)
        self.discord = Webhook.from_url(
            discord_webhook_url,
            adapter=AsyncWebhookAdapter(session)
        )

        self.logger.info("Initialized")

    async def start(self):
        """Scrape, send and save information about latest listings"""
        self.logger.info("Starting scraping...")
        while True:
            # Scrape
            fresh_listings = await self.scraper.scrape()

            # Check whether HTML looks as expected
            if not fresh_listings:
                warn_text = "fresh listings empty, HTML likely changed!"
                self.logger.warning(warn_text)
                await self.discord.send(f"{self.parsed_url.hostname} {warn_text}")
                await asyncio.sleep(self.N_SECONDS_SLEEP)
                continue

            # First, we need to find a listing that is present in both lists (fresh + old)
            first_mutual_listing_idx = self._find_first_mutual_listing_idx(fresh_listings)

            # If there are no mutual elements, all listings are new
            if first_mutual_listing_idx is None:
                first_mutual_listing_idx = len(fresh_listings)
                if self.listings:
                    self.logger.warning("All fresh listings are *NEW*")
                    # We need to warn the user that there might have been more listings added than
                    # we see in our LIMIT 20 request
                    await self.discord.send(
                        f"Next {first_mutual_listing_idx} listings from {self.parsed_url.hostname} "
                        "are all new, please check manually if there might be more."
                    )

            if self.listings:
                # If there are existing old listings
                # Send every new listing to discord starting from oldest to newest
                new_listings = fresh_listings[:first_mutual_listing_idx]
                for new_listing in reversed(new_listings):
                    if self.google_maps_api_key:
                        # Compute the distance from apartment to the given address
                        # in this case 'Rämistrasse, Zürich, Switzerland'
                        distance, duration = await compute_distance(
                            self.scraper.session,
                            self.google_maps_api_key,
                            new_listing.address
                        )
                    else:
                        distance, duration = None, None

                    await send_discord_listing_embed(
                        self.discord,
                        immo_data=new_listing,
                        hostname=self.parsed_url.hostname,
                        host_url=self.web_data["url"],
                        host_icon_url=self.web_data.get("author_icon_url"),
                        immo_distance=distance,
                        immo_duration=duration
                    )
                    self.logger.debug("sent %s", new_listing.url)
            else:
                # first scrape pass, there are no older listings yet
                self.logger.debug("skipping first batch of listings")

            # Save latest fresh listings
            self.listings = fresh_listings

            # wait
            await asyncio.sleep(self.N_SECONDS_SLEEP)

    def _find_first_mutual_listing_idx(self, fresh_listings: ImmoData):
        """Find the first index that is in both (old + fresh) listings"""
        for old_listing in self.listings:
            for i, fresh_listing in enumerate(fresh_listings):
                if old_listing.url == fresh_listing.url:
                    return i
