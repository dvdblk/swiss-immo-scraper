from dataclasses import (
    dataclass,
    fields,
    _MISSING_TYPE
)
from typing import List

@dataclass
class ImmoData:
    title: str
    url: str
    images: List[str]
    address: str = "No address"
    rent: str = "On request"
    rooms: str = "-"
    living_space: str = "-"

    def __post_init__(self):
        # Set default values properly for None
        # https://stackoverflow.com/a/69944614/4249857
        for field in fields(self):
            # Set a default value if the value of the field is None
            if not isinstance(field.default, _MISSING_TYPE) and getattr(self, field.name) is None:
                setattr(self, field.name, field.default)

        self.rent = self._add_suffix(self.rent, " CHF")
        self.living_space = self._add_suffix(self.living_space, " m²")

    def _add_suffix(self, x, suffix):
        """Add unit as a suffix to a given variable"""
        if not isinstance(x, str):
            x = str(x)

        if x.isdigit():
            x += suffix

        return x
