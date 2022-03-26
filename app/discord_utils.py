from datetime import datetime

from discord import Embed


async def send_discord_listing_embed(immo_data: ImmoData):
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
            value=f"{immo_data.rent} CHF",
            inline=True
        )
        embed.add_field(
            name="Rooms",
            value=immo_data.rooms,
            inline=True
        )
        living_space = immo_data.living_space
        if living_space != "-" and not living_space.endswith(" m²"):
            living_space += " m²"
        embed.add_field(
            name="Living space",
            value=living_space,
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