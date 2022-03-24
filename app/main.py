"""Main module"""
import argparse
import asyncio
import aiohttp
import json
from bs4 import BeautifulSoup


async def main(args: dict):
    """Starts the scraper"""
    urls = json.load(args.file)
    print(urls)

    async with aiohttp.ClientSession() as session:
        async with session.get(urls[0]["url"]) as resp:
            text = await resp.read()
            site = BeautifulSoup(text.decode('utf-8'), 'html.parser')
            print(site.find_all("article")[0])

if __name__=="__main__":

    parser = argparse.ArgumentParser(description="Swiss Immo Scraper")
    parser.add_argument(
        "-f",
        "--file",
        help="The json file with urls to scrape",
        type=argparse.FileType('r'),
        required=True
    )

    asyncio.run(main(parser.parse_args()))
