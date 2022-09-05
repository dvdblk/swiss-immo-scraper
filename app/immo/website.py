"""Swiss Immobilien websites enumeration"""
from enum import Enum

class ImmoWebsite(Enum):
    """Swiss Immobilien websites"""
    IMMOSCOUT24 = "www.immoscout24.ch"
    HOMEGATE = "www.homegate.ch"

    @property
    def author_icon_url(self) -> str:
        """Return thumbnail URL depending on current enum value"""
        match self.value:
            case ImmoWebsite.IMMOSCOUT24:
                return "https://play-lh.googleusercontent.com/FMd98MJtJLEo0uEDJtT8Gbs_fRjUV8aoVPpXcPTlZQwYL16vSh4XM2-y_X_-AYhQeMc"
            case ImmoWebsite.HOMEGATE:
                return "https://yt3.ggpht.com/ytc/AKedOLSoh7FW3igKCBh1866eXYyNt87wjZ4QJLXMvn3S5g=s900-c-k-c0x00ffffff-no-rj"
