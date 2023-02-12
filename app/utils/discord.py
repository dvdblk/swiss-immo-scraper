from ctypes import c_uint64
from datetime import datetime
from functools import reduce
from io import BytesIO
from typing import List, Tuple

import aiohttp
from discord import Embed, File, Webhook

from app.immo.model import ImmoData


async def _images_viewable_in_embed(
    images: List[str], session: aiohttp.ClientSession
) -> Tuple[List[str], List[File]]:
    """Discord Embeds only display image URLs that end with .jpeg
    or response has proper 'Content-Type'. This method downloads an
    image at a URL that doesn't obey these rules and then uploads it
    to the discord embed instead of passing a URL.

    https://discordpy.readthedocs.io/en/stable/faq.html#local-image

    Args:
        images: list of images (from ImmoData)
        session: shared aiohttp client session

    Returns:
        list of URLs: which can be local (e.g. attachment://<hash>) or
                        external (e.g. https://...)
        list of files: empty list for external urls, list of File for local
    """
    # Check if any of the image URLs ends with .jpg
    should_use_local_images = reduce(
        lambda seed, rest: seed or not rest.endswith(".jpg"), images, False
    )

    if should_use_local_images:
        local_images, image_files = [], []
        # do this for every image
        for image_url in images:
            resp = await session.get(image_url)
            image_data = BytesIO(await resp.read())
            local_image_url = f"{c_uint64(hash(image_url)).value:0x}.jpg"
            local_images.append(f"attachment://{local_image_url}")
            image_files.append(File(fp=image_data, filename=local_image_url))
        return local_images, image_files
    else:
        return images, []


async def send_discord_listing_embed(
    webhook: Webhook,
    session: aiohttp.ClientSession,
    immo_data: ImmoData,
    hostname: str,
    host_url: str,
    host_icon_url: str,
    immo_distance: str,
    immo_duration: str,
):
    """Sends an embed message from listing (immo) data"""
    embeds = []

    embed = Embed(
        title=immo_data.title,
        url=immo_data.url,
        color=5373709,
        timestamp=datetime.utcnow(),
    )
    embed.set_author(name=hostname, url=host_url, icon_url=host_icon_url or "")
    embed.add_field(name=immo_data.price_kind.value, value=immo_data.price, inline=True)
    embed.add_field(name="Rooms", value=immo_data.rooms, inline=True)
    embed.add_field(name="Living space", value=immo_data.living_space, inline=True)
    if immo_distance and immo_duration:
        # Add embed for distance and travel duration if possible
        embed.add_field(
            name="Distance", value=f"{immo_distance} ({immo_duration})", inline=True
        )
    embed.set_footer(text=immo_data.address)

    images, files = await _images_viewable_in_embed(immo_data.images, session)

    n_images = min(len(images), 4)
    if n_images > 0:
        embed.set_image(url=images[0])
    # Save first embed
    embeds.append(embed)

    # If we get more thumbnails, add more embeds
    if n_images > 1:
        for i in range(1, n_images):
            img_embed = Embed(url=immo_data.url)
            img_embed.set_image(url=images[i])
            embeds.append(img_embed)

    await webhook.send(embeds=embeds, files=files)
