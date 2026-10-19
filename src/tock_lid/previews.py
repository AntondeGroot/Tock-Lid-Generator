"""The font and style combinations shown in the README images."""

from dataclasses import dataclass
from pathlib import Path

from tock_lid.design import STYLES, LidSpec, find_style
from tock_lid.export import OverviewRow, overview_svg
from tock_lid.generator import LidSet, design_lids
from tock_lid.lettering import CATALOGUE, find_font

SHORTLIST = ("bodoni", "hoefler-black", "hoefler-black-italic", "bigcaslon", "superclarendon-black")


@dataclass(frozen=True)
class PreviewSheet:
    file_name: str
    fonts: tuple[str, ...]
    styles: tuple[str, ...]


PREVIEW_SHEETS = (
    PreviewSheet("fonts.svg", tuple(CATALOGUE), ("standard",)),
    PreviewSheet("styles.svg", SHORTLIST, tuple(STYLES)),
)


def write_preview_sheets(out_dir: Path, words: tuple[str, ...], lid: LidSpec) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for sheet in PREVIEW_SHEETS:
        path = out_dir / sheet.file_name
        path.write_text(overview_svg(overview_rows(sheet.fonts, sheet.styles, words, lid), lid))
        paths.append(path)
    return paths


def overview_rows(
    font_keys: tuple[str, ...], style_keys: tuple[str, ...], words: tuple[str, ...], lid: LidSpec
) -> list[OverviewRow]:
    rows = []
    for font_key in font_keys:
        font = find_font(font_key)
        for style_key in style_keys:
            style = find_style(style_key)
            lids = design_lids(LidSet(font, style, words, lid))
            rows.append(OverviewRow(f"{font.name}: {style.name} ({style.describe()})", list(lids.values())))
    return rows
