from __future__ import annotations

import asyncio
from typing import List, Optional
from urllib.parse import urlparse

from aiohttp import ClientSession
from discord import Webhook, AsyncWebhookAdapter

from app import setup_custom_logger
from app.immo.model import ImmoData
from app.immo.parser import ImmoParser, ImmoParserError
from app.immo.website import ImmoWebsite
from app.scraper import Scraper, ScraperNetworkError
from app.utils.discord import send_discord_listing_embed
from app.utils.google_maps import compute_distance


class ImmoManager:
    """Manage scraping apartment and estate listings every n seconds while posting new ones to Discord."""

    def __init__(
        self,
        immo_website_url: str,
        session: ClientSession,
        discord_webhook_url: str,
        n_seconds_sleep: int,
        google_maps_destination: Optional[str],
        google_maps_api_key: Optional[str] = None,
    ):
        """
        Args:
            immo_website_url: the URL this manager will scrape
            session: shared aiohttp.ClientSession
            discord_webhook_url: URL string of a discord webhook
            google_maps_destination: human readable destination string (e.g. "Raemistrasse, Zurich")
            google_maps_api_key: Google Maps API Key
        """
        self.immo_website_url = immo_website_url
        self.session = session
        self.google_maps_api_key = google_maps_api_key
        self.google_maps_destination_address = google_maps_destination
        self.n_seconds_sleep = n_seconds_sleep

        # Model
        parsed_url = urlparse(immo_website_url)
        hostname = parsed_url.hostname
        self.immo_website = ImmoWebsite(hostname)
        self.listings = None

        # Instances
        self.logger = setup_custom_logger(".".join([__name__, hostname]))
        self.scraper = Scraper(url=immo_website_url, session=session)
        self.discord = Webhook.from_url(
            discord_webhook_url, adapter=AsyncWebhookAdapter(session)
        )

        self.logger.info(f"Initialized for scraping: {immo_website_url}")

    async def _send_discord_message(self, listing):
        """Send discord message via a webhook for the given listing data"""
        if self.google_maps_api_key:
            # Compute the distance from apartment address to the destination address
            # in this case, default destination address = 'Rämistrasse, Zürich, Switzerland'
            distance, duration = await compute_distance(
                self.scraper.session,
                self.google_maps_api_key,
                origin_address=listing.address,
                destination_address=self.google_maps_destination_address,
            )
        else:
            distance, duration = None, None

        await send_discord_listing_embed(
            self.discord,
            session=self.session,
            immo_data=listing,
            hostname=self.immo_website.value,
            host_url=self.immo_website_url,
            host_icon_url=self.immo_website.author_icon_url,
            immo_distance=distance,
            immo_duration=duration,
        )
        self.logger.debug("sent %s", listing.url)

    def _find_first_mutual_listing_idx(self, fresh_listings: ImmoData) -> Optional[int]:
        """Find the first index that is in both (old + fresh) listings"""
        for old_listing in self.listings:
            for i, fresh_listing in enumerate(fresh_listings):
                if old_listing.url == fresh_listing.url:
                    return i

    async def _process_fresh_listings(self, fresh_listings: List[ImmoData]):
        """Search through latest fresh_listings, tagging any new (previously unseen) listings
        and then posting them to Discord.
        """
        if self.listings:
            # If there are existing old listings
            # First, we need to find a listing that is present in both lists (fresh + old)
            first_mutual_listing_idx = self._find_first_mutual_listing_idx(
                fresh_listings
            )

            # If there are no mutual elements, all listings are new
            if first_mutual_listing_idx is None:
                first_mutual_listing_idx = len(fresh_listings)
                if self.listings:
                    self.logger.warning("All fresh listings are *NEW*")
                    # We need to warn the user that there might have been more listings added than
                    # we see in our LIMIT 20 request
                    await self.discord.send(
                        f"Next {first_mutual_listing_idx} listings from {self.immo_website.value} "
                        "are all new, please check manually if there might be more."
                    )
            # Send every new listing to discord starting from oldest to newest
            new_listings = fresh_listings[:first_mutual_listing_idx]
            for new_listing in reversed(new_listings):
                await self._send_discord_message(new_listing)
        elif self.listings is None:
            # first scrape pass, there are no older listings yet
            self.logger.debug("skipping first batch of listings")

        # Save latest fresh listings for the next iteration
        self.listings = fresh_listings

    async def start(self):
        """Scrape, send and save information about latest listings"""
        while True:
            try:
                # Scrape
                fresh_listings_html = await self.scraper.scrape()
                # Parse HTML into fresh listings
                fresh_listings = ImmoParser.parse_html(
                    self.immo_website, fresh_listings_html
                )
            except ScraperNetworkError as e:
                self.logger.warning(
                    f"Caught ScraperNetworkError, skipping this round of scraping: {e}"
                )
                await asyncio.sleep(self.n_seconds_sleep)
                continue
            except (KeyError, ImmoParserError) as e:
                self.logger.warning(f"Caught parsing error, html likely changed: {e}")
                await asyncio.sleep(self.n_seconds_sleep)
                continue

            await self._process_fresh_listings(fresh_listings)

            # wait
            await asyncio.sleep(self.n_seconds_sleep)
