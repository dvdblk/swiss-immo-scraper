"""Main module"""
import asyncio
from typing import Type

import sentry_sdk

from app import init_client_session, setup_custom_logger
from app.manager import ImmoManager
from app.config import Config


log = setup_custom_logger(__name__)


async def main(config: Config, manager_class: Type[ImmoManager] = ImmoManager):
    """Create an ImmoManager for each immo website and start scraping"""
    session = init_client_session()

    managers, tasks = [], []

    if not config.scrape_urls:
        log.info("No URLs for scraping provided. Exiting...")
        return

    for url in config.scrape_urls:
        manager = manager_class(
            immo_website_url=url,
            session=session,
            discord_webhook_url=config.discord_webhook,
            n_seconds_sleep=config.scraping_interval,
            google_maps_destination=config.google_maps_destination,
            google_maps_api_key=config.google_maps_api_key,
        )
        managers.append(manager)

        tasks.append(asyncio.create_task(manager.start()))

    # Wait for all tasks to finish (ideally never)
    await asyncio.gather(*tasks)

    await session.close()


if __name__ == "__main__":
    # Load the ENV Variables into a config instance
    config = Config()

    # Setup Sentry if needed
    if dsn := config.sentry_dsn:
        sentry_sdk.init(
            dsn=dsn, traces_sample_rate=1.0, ignore_errors=[KeyboardInterrupt]
        )

    asyncio.run(main(config))
