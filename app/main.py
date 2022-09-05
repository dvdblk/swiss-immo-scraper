"""Main module"""
import asyncio

from app import init_client_session, setup_custom_logger
from app.manager import ImmoManager
from app.config import Config


log = setup_custom_logger(__name__)

async def main(config: Config):
    """Create an ImmoManager for each immo website and start scraping"""
    session = init_client_session()

    managers, tasks = [], []

    if not config.scrape_urls:
        log.info("No URLs for scraping provided. Exiting...")
        return

    for url in config.scrape_urls:
        manager = ImmoManager(
            immo_website_url=url,
            session=session,
            discord_webhook_url=config.discord_webhook,
            google_maps_destination=config.google_maps_destination,
            google_maps_api_key=config.google_maps_api_key
        )
        managers.append(manager)

        tasks.append(
            asyncio.create_task(manager.start())
        )

    # Wait for all tasks to finish (never)
    await asyncio.gather(*tasks)


if __name__=="__main__":
    # Load the ENV Variables into a config instance
    config = Config()

    asyncio.run(main(config))
