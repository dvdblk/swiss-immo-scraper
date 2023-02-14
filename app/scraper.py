from aiohttp import (
    ClientConnectionError,
    ClientConnectorError,
    ClientOSError,
    ClientSession,
    ServerDisconnectedError,
)
from bs4 import BeautifulSoup


class ScraperNetworkError(Exception):
    """Scraping network exceptions"""

    pass


class Scraper:
    """Fetch the given url and return scraped data"""

    def __init__(self, url: str, session: ClientSession) -> None:
        self.url = url
        self.session = session

    async def scrape(self) -> BeautifulSoup:
        """Download the HTML and load it into a soup"""
        try:
            resp = await self.session.get(self.url)
            if resp.status == 200:
                html = await resp.read()
                return BeautifulSoup(html.decode("utf-8"), "html.parser")
            else:
                raise ScraperNetworkError(f"status={resp.status}")
        except (
            ClientConnectorError,
            ClientOSError,
            ClientConnectionError,
            ServerDisconnectedError,
        ) as err:
            raise ScraperNetworkError from err
