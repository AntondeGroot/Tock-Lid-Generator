"""Catalogue of macOS system fonts that print well as outlined lid text."""

from dataclasses import dataclass
from pathlib import Path

SUPPLEMENTAL = Path("/System/Library/Fonts/Supplemental")
SYSTEM = Path("/System/Library/Fonts")


@dataclass(frozen=True)
class FontFace:
    name: str
    path: Path
    index: int = 0  # face number inside a .ttc collection
    uppercase: bool = False


CATALOGUE: dict[str, FontFace] = {
    "bodoni": FontFace("Bodoni 72 Bold", SUPPLEMENTAL / "Bodoni 72.ttc", 2),
    "bodoni-caps": FontFace("Bodoni 72 Bold, capitals", SUPPLEMENTAL / "Bodoni 72.ttc", 2, uppercase=True),
    "bodoni-italic": FontFace("Bodoni 72 Book Italic", SUPPLEMENTAL / "Bodoni 72.ttc", 1),
    "bodoni-smallcaps": FontFace("Bodoni 72 Smallcaps", SUPPLEMENTAL / "Bodoni 72 Smallcaps Book.ttf"),
    "hoefler-black": FontFace("Hoefler Text Black", SUPPLEMENTAL / "Hoefler Text.ttc", 1),
    "hoefler-black-italic": FontFace("Hoefler Text Black Italic", SUPPLEMENTAL / "Hoefler Text.ttc", 3),
    "bigcaslon": FontFace("Big Caslon", SUPPLEMENTAL / "BigCaslon.ttf"),
    "baskerville-bold-italic": FontFace("Baskerville Bold Italic", SUPPLEMENTAL / "Baskerville.ttc", 3),
    "iowan-black": FontFace("Iowan Old Style Black", SUPPLEMENTAL / "Iowan Old Style.ttc", 4),
    "palatino-bold-italic": FontFace("Palatino Bold Italic", SYSTEM / "Palatino.ttc", 3),
    "cochin": FontFace("Cochin Bold Italic", SUPPLEMENTAL / "Cochin.ttc", 3),
    "didot": FontFace("Didot Bold", SUPPLEMENTAL / "Didot.ttc", 2),
    "superclarendon-black": FontFace("Superclarendon Black", SUPPLEMENTAL / "SuperClarendon.ttc", 7),
    "superclarendon-black-italic": FontFace(
        "Superclarendon Black Italic", SUPPLEMENTAL / "SuperClarendon.ttc", 6
    ),
    "rockwell-bold": FontFace("Rockwell Bold", SUPPLEMENTAL / "Rockwell.ttc", 2),
    "copperplate": FontFace("Copperplate Bold", SUPPLEMENTAL / "Copperplate.ttc", 2),
    "phosphate": FontFace("Phosphate Solid", SUPPLEMENTAL / "Phosphate.ttc", 1),
    "snell": FontFace("Snell Roundhand Black", SUPPLEMENTAL / "SnellRoundhand.ttc", 2),
    "signpainter": FontFace("SignPainter Semibold", SUPPLEMENTAL / "SignPainter.ttc", 1),
    "brushscript": FontFace("Brush Script", SUPPLEMENTAL / "Brush Script.ttf"),
    "chancery": FontFace("Apple Chancery", SUPPLEMENTAL / "Apple Chancery.ttf"),
    "trattatello": FontFace("Trattatello", SUPPLEMENTAL / "Trattatello.ttf"),
    "luminari": FontFace("Luminari", SUPPLEMENTAL / "Luminari.ttf"),
    "herculanum": FontFace("Herculanum", SUPPLEMENTAL / "Herculanum.ttf"),
    "optima-black": FontFace("Optima ExtraBlack", SYSTEM / "Optima.ttc", 4),
    "futura-condensed": FontFace("Futura Condensed ExtraBold", SUPPLEMENTAL / "Futura.ttc", 4),
}


def find_font(key: str) -> FontFace:
    try:
        return CATALOGUE[key]
    except KeyError:
        known = ", ".join(CATALOGUE)
        raise ValueError(f"Unknown font '{key}'. Known fonts: {known}") from None


def font_from_file(path: Path, index: int = 0) -> FontFace:
    """Any .ttf/.otf/.ttc on disk, for fonts outside the catalogue."""
    if not path.is_file():
        raise ValueError(f"Font file not found: {path}")
    return FontFace(path.stem, path, index)
