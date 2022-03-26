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
        write_to_clipboard(json.dumps(listings))

        articles = html.find_all("article")
        listings = []
        for article in articles:
            if article.get("data-property-id") is not None:
                listings.append(article)

        immo_data_list = []
        for listing in listings:
            info_tag = listing.find("div", { "class": re.compile("^Content-") })
            title_raw = info_tag.find("div").h2.text
            title = title_raw.replace("<!-- -->", "").replace("«", "").replace("»", "")

            address = info_tag.find("span", { "class": re.compile("^AddressLine") }).text
            url = listing.a["href"]

            stats_raw = info_tag.h3.text.replace("<!-- -->", "").replace("<span>", "").replace("</span>", "")
            stats = stats_raw.split(",")
            rooms, rent, living_space = None, None, None
            for stat in stats:
                if "rooms" in stat:
                    rooms = stat.rstrip(" rooms")
                elif "CHF" in stat:
                    rent = stat.lstrip("CHF ").rstrip(".—")
                elif "m²" in stat:
                    living_space = stat

            image_divs = listing.find_all("div", { "class": re.compile("^Slide-") })
            image_tags = list(map(lambda d: d.img, image_divs))
            if len(image_tags) > 1:
                # Remove first image of index(last_img) if needed
                if image_tags[0] in image_tags[1:]:
                    del image_tags[0]

            n_images = len(image_tags)
            if n_images > 1:
                # Remove duplicate 0 index image if needed
                if image_tags[n_images-1] in image_tags[:n_images-1]:
                    del image_tags[n_images-1]

            images = list(map(lambda img: img["src"], image_tags))

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
