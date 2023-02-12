"""Swiss Immobilien websites enumeration"""
from enum import Enum


class ImmoWebsite(Enum):
    """Swiss Immobilien websites"""

    IMMOSCOUT24 = "www.immoscout24.ch"
    HOMEGATE = "www.homegate.ch"
    IMMOBILIENSCOUT24AT = "www.immobilienscout24.at"
    IMMODIREKTAT = "www.immodirekt.at"
    IMMOWELTAT = "www.immowelt.at"

    @property
    def author_icon_url(self) -> str:
        """Return thumbnail URL depending on current enum value"""
        match self:
            case ImmoWebsite.IMMOSCOUT24:
                return "https://play-lh.googleusercontent.com/9qHvJvi4zgrXzfhsDlJpyU2JEaadxVtLOy0zg3vUNQTAJhZFroCcXObWMEhlhf_sOkQ"
            case ImmoWebsite.HOMEGATE:
                return "https://yt3.ggpht.com/ytc/AKedOLSoh7FW3igKCBh1866eXYyNt87wjZ4QJLXMvn3S5g=s900-c-k-c0x00ffffff-no-rj"
            case ImmoWebsite.IMMOBILIENSCOUT24AT:
                return ImmoWebsite.IMMOSCOUT24.author_icon_url
            case ImmoWebsite.IMMODIREKTAT:
                return "https://www.immodirekt.at/assets/images/favicon.ico"
            case ImmoWebsite.IMMOWELTAT:
                return "https://cdnglobal.immowelt.org/residential-search-ui/6.14.2/favicon.ico"
