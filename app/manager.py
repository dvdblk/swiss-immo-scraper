"""Manager for scraping individual immo websites and sending discord messages"""
import asyncio
from urllib.parse import urlparse
from datetime import date, datetime

from aiohttp import ClientSession
from discord import (
    Webhook,
    AsyncWebhookAdapter,
    Embed
)

from app import immo, setup_custom_logger
from app.scraper import Scraper
from app.immo.model import ImmoData


class ImmoManager:
    """do stuff"""
    # Time delta between individual scrapes
    N_SECONDS_SLEEP = 120

    def __init__(self, web_data: dict, session: ClientSession, discord_webhook_url: str):
        self.web_data = web_data
        self.parsed_url = urlparse(web_data["url"])
        self.logger = setup_custom_logger(".".join([__name__, self.parsed_url.hostname]))
        self.listings = []
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

            # if self.listings:
                # If there are existing old listings
                # Send every new listing to discord starting from oldest to newest
            new_listings = fresh_listings[:first_mutual_listing_idx]
            for new_listing in reversed(fresh_listings[:2]):
                await self.send_discord_listing_embed(immo_data=new_listing)
                self.logger.debug("sent %s", new_listing.url)
            # else:
            #     # first pass, there are no older listings
            #     self.logger.debug("skipping first batch of listings")

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

    async def send_discord_listing_embed(self, immo_data: ImmoData):
        """Sends an embed message from listing (immo) data"""
        embeds = []

        embed = Embed(
            title=immo_data.title,
            url=immo_data.url,
            color=5373709,
            timestamp=datetime.utcnow()
        )
        embed.set_author(
            name=self.parsed_url.hostname,
            url=f"https://{self.parsed_url.hostname}",
            icon_url=self.web_data["author_icon_url"]
        )
        embed.add_field(
            name="Rent",
            value=immo_data.rent,
            inline=True
        )
        embed.add_field(
            name="Rooms",
            value=immo_data.rooms,
            inline=True
        )
        embed.add_field(
            name="Living space",
            value=immo_data.living_space,
            inline=True
        )
        embed.set_footer(
            text=immo_data.address
        )

        n_images = min(len(immo_data.images), 4)
        if n_images > 0:
            embed.set_image(url=immo_data.images[0])
        # Save first embed
        embeds.append(embed)

        # If we get more thumbnails, add more embeds
        if n_images > 1:
            for i in range(1, n_images):
                img_embed = Embed(url=immo_data.url)
                img_embed.set_image(url=immo_data.images[i])
                embeds.append(img_embed)

        await self.discord.send(embeds=embeds)
