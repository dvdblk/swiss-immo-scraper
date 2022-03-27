"""Scraping functionality"""
from urllib.parse import ParseResult

from aiohttp import (
    ClientSession,
    ClientConnectorError
)
from bs4 import BeautifulSoup

from app.immo.website import ImmoWebsite
from app.immo.parser import ImmoParser
from app.immo.model import ImmoData

class ScraperError(Exception):
    """Scraping exceptions"""
    pass


class Scraper:
    """Fetch the given url and return scraped data"""

    def __init__(self, parsed_url: ParseResult, session: ClientSession) -> None:
        # Web data can contain user agent etc...
        self.url = parsed_url.geturl()
        self.website = ImmoWebsite(parsed_url.hostname)
        self.session = session

    async def _fetch(self):
        """Download the HTML and load it into a soup"""
        try:
            resp = await self.session.get(self.url)
            if resp.status == 200:
                html = await resp.read()
                return BeautifulSoup(html.decode("utf-8"), "html.parser")
            else:
                raise ScraperError(f"status={resp.status}")
        except ClientConnectorError as err:
            raise ScraperError from err

    async def scrape(self) -> list[ImmoData]:
        """Scrape the given website data and return a list of last x listings"""
        html = await self._fetch()
        return ImmoParser.parse_html(self.website, html)
