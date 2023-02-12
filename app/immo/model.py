from dataclasses import dataclass, fields, _MISSING_TYPE
from enum import Enum
from typing import List


class ImmoPriceKind(Enum):
    """Enumeration for the different price kinds for an Immo object"""

    RENT = "Rent"
    PRICE = "Price"


@dataclass
class ImmoData:
    title: str
    url: str
    images: List[str]
    address: str = "No address"
    price: str = "On request"
    price_kind: ImmoPriceKind = ImmoPriceKind.RENT
    rooms: str = "-"
    living_space: str = "-"
    currency: str = "CHF"

    def __post_init__(self):
        # Set default values properly for None input arguments
        # https://stackoverflow.com/a/69944614/4249857
        for field in fields(self):
            # Set a default value if the value of the field is None
            if (
                not isinstance(field.default, _MISSING_TYPE)
                and getattr(self, field.name) is None
            ):
                setattr(self, field.name, field.default)

        self.price = self._add_suffix(self.price, f" {self.currency}")
        self.living_space = self._add_suffix(self.living_space, " m²")

        if isinstance(self.rooms, int):
            self.rooms = str(self.rooms)

    def _add_suffix(self, x, suffix) -> str:
        """Add unit as a suffix to a given variable"""
        if not isinstance(x, str):
            x = str(x)

        if x.isdigit():
            x += suffix

        return x
