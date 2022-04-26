from datetime import datetime

from discord import (
    Embed,
    Webhook
)

from app.immo.model import ImmoData


async def send_discord_listing_embed(
    webhook: Webhook, immo_data: ImmoData, hostname: str, host_url: str,
    host_icon_url: str, immo_distance: str, immo_duration: str
):
    """Sends an embed message from listing (immo) data"""
    embeds = []

    embed = Embed(
        title=immo_data.title,
        url=immo_data.url,
        color=5373709,
        timestamp=datetime.utcnow()
    )
    embed.set_author(
        name=hostname,
        url=host_url,
        icon_url=host_icon_url or ""
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
    if immo_distance and immo_duration:
        # Add embed for distance and travel duration if possible
        embed.add_field(
            name="Distance",
            value=f"{immo_distance} ({immo_duration})",
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

    await webhook.send(embeds=embeds)