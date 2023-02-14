import asyncio
from typing import List

from app.config import Config
from app.main import main
from app.manager import ImmoManager
from app.immo.model import ImmoData


class PreviewImmoManager(ImmoManager):
    async def _process_fresh_listings(self, fresh_listings: List[ImmoData]):
        if fresh_listings:
            self.logger.debug("Preview mode: sending preview to Discord...")
            await self._send_discord_message(fresh_listings[0])
        else:
            self.logger.debug(
                "Preview mode: no listings found while scraping (fresh_listings is empty)."
            )


if __name__ == "__main__":
    config = Config()

    asyncio.run(main(config, PreviewImmoManager))
