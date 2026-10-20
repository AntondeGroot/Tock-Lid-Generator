"""Catalogue of fonts that print well as outlined lid text.

Three free fonts ship with the package and work everywhere; the rest are macOS system fonts
that are only offered on a computer that has them."""

from dataclasses import dataclass
from pathlib import Path

BUNDLED = Path(__file__).parent.parent / "fonts"
SUPPLEMENTAL = Path("/System/Library/Fonts/Supplemental")
SYSTEM = Path("/System/Library/Fonts")


@dataclass(frozen=True)
class FontFace:
    name: str
    path: Path
    index: int = 0  # face number inside a .ttc collection
    uppercase: bool = False

    @property
    def is_bundled(self) -> bool:
        return self.path.is_relative_to(BUNDLED)

    @property
    def is_available(self) -> bool:
        return self.path.is_file()


CATALOGUE: dict[str, FontFace] = {
    # Free (SIL Open Font License), shipped in tock_lid/fonts
    "playball": FontFace("Playball", BUNDLED / "playball" / "Playball-Regular.ttf"),
    "norican": FontFace("Norican", BUNDLED / "norican" / "Norican-Regular.ttf"),
    "spectral-extrabold-italic": FontFace(
        "Spectral ExtraBold Italic", BUNDLED / "spectral" / "Spectral-ExtraBoldItalic.ttf"
    ),
    # macOS system fonts
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
    "luminari": FontFace("Luminari", SUPPLEMENTAL / "Luminari.ttf"),
    "optima-black": FontFace("Optima ExtraBlack", SYSTEM / "Optima.ttc", 4),
    "futura-condensed": FontFace("Futura Condensed ExtraBold", SUPPLEMENTAL / "Futura.ttc", 4),
}


def available_fonts() -> dict[str, FontFace]:
    """The catalogue entries whose font file exists on this computer."""
    return {key: font for key, font in CATALOGUE.items() if font.is_available}


def find_font(key: str) -> FontFace:
    font = CATALOGUE.get(key)
    if font is not None and font.is_available:
        return font
    here = ", ".join(available_fonts())
    if font is not None:
        raise ValueError(f"'{key}' is a macOS font and is not on this computer. Available here: {here}")
    raise ValueError(f"Unknown font '{key}'. Available here: {here}")


def file_label(font_key: str) -> str:
    """Short font name for file names: the part before the first dash, e.g. 'hoefler'."""
    before_dash, _, _ = font_key.partition("-")
    return before_dash.lower()


def font_from_file(path: Path, index: int = 0) -> FontFace:
    """Any .ttf/.otf/.ttc on disk, for fonts outside the catalogue."""
    if not path.is_file():
        raise ValueError(f"Font file not found: {path}")
    return FontFace(path.stem, path, index)
