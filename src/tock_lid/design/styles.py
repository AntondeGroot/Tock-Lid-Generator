"""Outline styles: the rings drawn around the letters, from the letter outward."""

from dataclasses import dataclass

RED = "#d62828"
BLACK = "#000000"
CREAM = "#f1e9d8"
WHITE = "#ffffff"


@dataclass(frozen=True)
class Ring:
    name: str
    width_mm: float
    colour: str


@dataclass(frozen=True)
class Style:
    name: str
    rings: tuple[Ring, ...]
    fill_colour: str = RED
    background_colour: str = WHITE

    def describe(self) -> str:
        return " + ".join(f"{ring.width_mm} mm" for ring in self.rings)


STYLES: dict[str, Style] = {
    "standard": Style("standard", (Ring("outline", 0.8, BLACK),)),
    "thick": Style("thick", (Ring("outline", 1.6, BLACK),)),
    "double": Style(
        "double",
        (
            Ring("outline-inner", 0.8, BLACK),
            Ring("gap", 0.8, CREAM),
            Ring("outline-outer", 0.8, BLACK),
        ),
    ),
}


def find_style(key: str) -> Style:
    try:
        return STYLES[key]
    except KeyError:
        known = ", ".join(STYLES)
        raise ValueError(f"Unknown style '{key}'. Known styles: {known}") from None
