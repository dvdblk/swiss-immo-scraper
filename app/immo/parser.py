"""Parsing for immobilien websites"""
from asyncore import write
import json
import subprocess
import re
from urllib.parse import urljoin
from typing import List

from bs4 import BeautifulSoup

from app.immo.website import ImmoWebsite
from app.immo.model import ImmoData

class ImmoParserError(Exception):
    """Parsing errors"""
    ...


def write_to_clipboard(output):
        process = subprocess.Popen(
            'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
        process.communicate(output.encode('utf-8'))


def scaled_image_size(width, height, max_width, max_height):
    """Resize the image given original w/h given max w/h

    Note:
        https://stackoverflow.com/a/6501997/4249857
    """
    # Set default w/h if given is == 0
    if not width:
        width = 1024
    if not height:
        height = 728

    ratio_x = max_width / width
    ratio_y = max_height / height
    ratio = min(ratio_x, ratio_y)

    return width * ratio, height * ratio


class ImmoParser:
    """Parse different HTML Immo website listings"""

    @staticmethod
    def _parse_immoscout24(html: BeautifulSoup) -> List[ImmoData]:
        """Parse immoscout24.ch listings

        Returns:
            List[str]: url paths of listings on the immo website
        """
        json_data_raw = html.find("script", { "id": "state" }).text.lstrip("__INITIAL_STATE__=")
        # This data contains obfuscated js code, need to clean it up first
        json_data_clean = re.sub(
            pattern='("insertion":{.*)("maxPriceCalculator")',
            repl="\\2",
            string=json_data_raw
        )
        json_data_clean = re.sub(
            pattern=":undefined",
            repl=":null",
            string=json_data_clean
        )
        listings_json = json.loads(json_data_clean)
        listings = listings_json["pages"]["searchResult"]["resultData"]["listData"]

        immo_data_list = []
        for listing in listings:
            title = listing.get("title", "Wohnung")
            try:
                loc = listing["cityName"]
                plz = listing["zip"]
                street = listing["street"]
                state = listing["stateShort"]
                address = f"{street}, {plz} {loc}, {state}"
            except KeyError:
                address = None
            url = listing.get("propertyUrl")
            rent = listing.get("price")
            rooms = listing.get("numberOfRooms")
            living_space = listing.get("surfaceLiving")

            images = []
            for img in listing.get("images", []):
                width, height = scaled_image_size(
                    img["originalWidth"],
                    img["originalHeight"],
                    1280,
                    720
                )
                images.append(
                    img["url"]\
                    .replace("{width}", str(width), 1)\
                    .replace("{height}", str(height), 1)\
                    .replace("{resizemode}", "3", 1)\
                    .replace("{quality}", "90", 1)
                )

            immo_data_list.append(
                ImmoData(
                    title=title,
                    address=address,
                    url=url,
                    rent=rent,
                    rooms=rooms,
                    living_space=living_space,
                    images=images
                )
            )

        return immo_data_list

    @staticmethod
    def _parse_homegate(html: BeautifulSoup) -> List[ImmoData]:
        """Parse homegate.ch listings

        Returns:
            List[str]: url paths of listings on the immo website
        """
        results = html.find("div", { "data-test": "result-list" })
        listings = list(map(lambda listing: listing.a, results.children))

        script_tags = html.find_all("script")
        text_to_lstrip = "window.__INITIAL_STATE__="
        listings_json = None
        for script_tag in script_tags:
            if script_tag.text.startswith(text_to_lstrip):
                listings_json = json.loads(script_tag.text.lstrip(text_to_lstrip))

        if listings_json is None:
            raise ImmoParserError(
                "Can't find homegate.ch <script> with JSON data in HTML"
            )

        listings = listings_json\
            ["resultList"]["search"]["fullSearch"]["result"]["listings"]

        immo_data_list = []
        for listing in listings:
            listing = listing["listing"]
            localization = listing["localization"]
            primary_key = localization["primary"]
            title = localization[primary_key]["text"]["title"]
            images_list = localization[primary_key]["attachments"]
            images = []
            for image_obj in images_list:
                if image_obj["type"] == "IMAGE":
                    images.append(
                        image_obj["url"].encode().decode("unicode-escape")
                    )
            address = None
            try:
                loc = listing["address"]["locality"]
                plz = listing["address"]["postalCode"]
                street = listing["address"]["street"]
                address = f"{street}, {plz} {loc}"
            except KeyError:
                pass
            url = f"/rent/{listing['id']}"
            rent = listing["prices"]["rent"].get("gross")
            rooms = str(listing["characteristics"].get("numberOfRooms"))
            living_space = listing["characteristics"].get("livingSpace")

            immo_data_list.append(
                ImmoData(
                    title=title,
                    address=address,
                    url=url,
                    rent=rent,
                    rooms=rooms,
                    living_space=living_space,
                    images=images
                )
            )

        return immo_data_list

    @classmethod
    def parse_html(cls, website: ImmoWebsite, html: BeautifulSoup) -> List[ImmoData]:
        """Select the correct parser and parse the given html

        Returns:
            immo_data: list of data about each listing
        """
        results = None
        match website:
            case ImmoWebsite.IMMOSCOUT24:
                results = cls._parse_immoscout24(html)
            case ImmoWebsite.HOMEGATE:
                results = cls._parse_homegate(html)

        for immo_data in results:
            immo_data.url = f"https://{website.value}{immo_data.url}"

        return results
