"""Parsing for immobilien websites"""
import json
import re

from bs4 import BeautifulSoup

from app.immo.website import ImmoWebsite
from app.immo.model import ImmoData
from app.image_utils import scaled_image_size
from app import setup_custom_logger


logger = setup_custom_logger(__name__)


class ImmoParserError(Exception):
    """Parsing errors"""
    pass


class ImmoParser:
    """Parse different HTML Immo website listings"""

    @staticmethod
    def _parse_immoscout24(html: BeautifulSoup) -> list[ImmoData]:
        """Parse immoscout24.ch listings

        Returns:
            list[ImmoData]: ImmoData of listings on the immo website
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
        try:
            listings = listings_json["pages"]["searchResult"]["resultData"]["listData"]
        except KeyError:
            raise ImmoParserError("Listings json changed.")

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
                # Need to set a valid size for the image to load (less than 1280x720)
                width, height = scaled_image_size(
                    img.get("originalWidth", 0),
                    img.get("originalHeight", 0),
                    1280,
                    720
                )
                if img.get("url"):
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
    def _parse_homegate(html: BeautifulSoup) -> list[ImmoData]:
        """Parse homegate.ch listings

        Returns:
            list[ImmoData]: ImmoData of listings on the immo website
        """
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

        try:
            listings = listings_json\
                ["resultList"]["search"]["fullSearch"]["result"]["listings"]
        except KeyError:
            raise ImmoParserError("Listings json changed.")
        except TypeError as e:
            raise ImmoParserError(str(e))

        immo_data_list = []
        for listing in listings:
            try:
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
                rooms, living_space = None, None
                if characteristics := listing.get("characteristics"):
                    rooms = str(characteristics.get("numberOfRooms"))
                    living_space = characteristics.get("livingSpace")

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
            except KeyError:
                logger.error("homegate.ch key error: %s", listing)
                continue


        return immo_data_list

    @classmethod
    def parse_html(cls, website: ImmoWebsite, html: BeautifulSoup) -> list[ImmoData]:
        """Select the correct parser and parse the given html

        Returns:
            list[immo_data]: list of data about each listing
        """
        match website:
            case ImmoWebsite.IMMOSCOUT24:
                results = cls._parse_immoscout24(html)
            case ImmoWebsite.HOMEGATE:
                results = cls._parse_homegate(html)

        for immo_data in results:
            immo_data.url = f"https://{website.value}{immo_data.url}"

        return results
