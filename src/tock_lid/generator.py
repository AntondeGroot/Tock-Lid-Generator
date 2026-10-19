"""Designing a set of lids (one per language) and writing their files."""

from dataclasses import dataclass
from pathlib import Path

from tock_lid.design import Layer, LidSpec, Style, fit_scale, lid_layers
from tock_lid.export import lid_svg, write_stl
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


def write_lid_files(word: str, layers: list[Layer], lid: LidSpec, out_dir: Path) -> Path:
    """A preview SVG plus, per colour, an SVG for CAD and an STL for the slicer."""
    folder = out_dir / word.lower()
    folder.mkdir(parents=True, exist_ok=True)
    (folder / f"{word.lower()}-preview.svg").write_text(lid_svg(layers, lid, guide=True))
    for layer in layers:
        stem = folder / f"{word.lower()}-{layer.name}"
        stem.with_suffix(".svg").write_text(lid_svg([layer], lid))
        write_stl(stem.with_suffix(".stl"), layer.shape, lid.thickness_mm)
    return folder
