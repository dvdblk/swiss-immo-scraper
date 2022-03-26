"""Main module"""
import argparse
import asyncio
import json
import os

import aiohttp

from dotenv import load_dotenv

from app.manager import ImmoManager


async def main(args: dict):
    """Starts the scraper"""
    load_dotenv()
    discord_webhook = os.getenv("DISCORD_WEBHOOK")

    session = aiohttp.ClientSession(
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:98.0) Gecko/20100101 Firefox/98.0"
        }
    )
    loop = asyncio.get_running_loop()

    managers = []
    scrape_data = json.load(args.file)
    for web_data in scrape_data:
        manager = ImmoManager(web_data, session, discord_webhook)
        managers.append(manager)

        loop.create_task(manager.start())

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Swiss Immo Scraper")
    parser.add_argument(
        "-f",
        "--file",
        help="The json file with urls to scrape",
        type=argparse.FileType("r"),
        required=True
    )

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.create_task(main(parser.parse_args()))
        loop.run_forever()
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
