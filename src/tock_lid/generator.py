"""Designing a set of lids (one per language) and writing their files."""

from dataclasses import dataclass
from pathlib import Path

from tock_lid.design import Layer, LidSpec, Style, fit_scale, lid_layers
from tock_lid.export import lid_svg, write_stl, write_svg
from tock_lid.lettering import FontFace, word_outline


@dataclass(frozen=True)
class LidSet:
    font: FontFace
    style: Style
    words: tuple[str, ...]
    lid: LidSpec


def design_lids(lid_set: LidSet) -> dict[str, list[Layer]]:
    """Word to its layers. All words share the largest letter size at which every word fits."""
    style, lid = lid_set.style, lid_set.lid
    outlines = {word: word_outline(lid_set.font, word) for word in lid_set.words}
    scale = min(fit_scale(outline, style, lid) for outline in outlines.values())
    return {word: lid_layers(outline, scale, style, lid) for word, outline in outlines.items()}


def lid_file_stem(word: str, font_label: str) -> str:
    """The start of every file name of one lid, e.g. 'keezen-hoefler'."""
    return f"{word.lower()}-{font_label}"


def write_lid_files(word: str, font_label: str, layers: list[Layer], lid: LidSpec, out_dir: Path) -> Path:
    """A preview SVG plus, per colour, an SVG for CAD and an STL for the slicer."""
    folder = out_dir / word.lower()
    folder.mkdir(parents=True, exist_ok=True)
    lid_stem = lid_file_stem(word, font_label)
    write_svg(folder / f"{lid_stem}-preview.svg", lid_svg(layers, lid, guide=True))
    for layer in layers:
        stem = folder / f"{lid_stem}-{layer.name}"
        write_svg(stem.with_suffix(".svg"), lid_svg([layer], lid))
        write_stl(stem.with_suffix(".stl"), layer.shape, lid.thickness_mm)
    return folder
