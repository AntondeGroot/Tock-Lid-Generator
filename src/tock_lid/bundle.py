"""A zip of lids as STL parts, so people can download them all and pick one."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from tock_lid.design import STYLES, Layer, LidSpec, find_style
from tock_lid.export import lid_svg
from tock_lid.export.stl import extrude
from tock_lid.generator import LidSet, design_lids
from tock_lid.lettering import CATALOGUE, find_font

ROOT_FOLDER = "tock-lids"
HOW_TO_PRINT = """\
Tock / Keezen lid inserts, one folder per font/style/word.

Each word folder holds one STL per colour, all sharing the centre of the lid:
  *-fill.stl         the letters
  *-outline*.stl     the outline ring(s); *-gap.stl is the space between double outlines
  *-background.stl   the rest of the disc
  *-preview.svg      what the colours look like together

In the slicer, select all STLs of one word, load them as ONE object with multiple parts,
then give each part its filament. Generated with https://github.com/AntondeGroot/Tock-Lid-Generator
"""


def every_font_and_style() -> list[tuple[str, str]]:
    return [(font, style) for font in CATALOGUE for style in STYLES]


def write_bundle(zip_path: Path, combinations: list[tuple[str, str]], words: tuple[str, ...], lid: LidSpec):
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(zip_path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(f"{ROOT_FOLDER}/HOW-TO-PRINT.txt", HOW_TO_PRINT)
        for font_key, style_key in combinations:
            lid_set = LidSet(find_font(font_key), find_style(style_key), words, lid)
            for word, layers in design_lids(lid_set).items():
                folder = f"{ROOT_FOLDER}/{font_key}/{style_key}/{word.lower()}"
                _add_lid(archive, folder, word.lower(), layers, lid)


def _add_lid(archive: ZipFile, folder: str, stem: str, layers: list[Layer], lid: LidSpec) -> None:
    archive.writestr(f"{folder}/{stem}-preview.svg", lid_svg(layers, lid, guide=True))
    for layer in layers:
        stl = extrude(layer.shape, lid.thickness_mm).export(file_type="stl")
        archive.writestr(f"{folder}/{stem}-{layer.name}.stl", stl)
