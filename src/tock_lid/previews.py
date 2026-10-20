"""The font and style combinations shown in the README images."""

from dataclasses import dataclass
from pathlib import Path

from tock_lid.design import STYLES, LidSpec, find_style
from tock_lid.export import OverviewRow, overview_svg, write_svg
from tock_lid.generator import LidSet, design_lids
from tock_lid.lettering import CATALOGUE, find_font

# The favourites; the free fonts were chosen to stand in for them on other systems.
MACOS_FAVOURITES = ("snell", "hoefler-black-italic", "bodoni")


@dataclass(frozen=True)
class PreviewSheet:
    file_name: str
    fonts: tuple[str, ...]
    styles: tuple[str, ...]

    @property
    def can_be_drawn_here(self) -> bool:
        return all(CATALOGUE[key].is_available for key in self.fonts)


def preview_sheets() -> tuple[PreviewSheet, ...]:
    """The README sheets, grouped by where their fonts work."""
    everywhere = tuple(key for key, font in CATALOGUE.items() if font.is_bundled)
    macos_only = tuple(key for key, font in CATALOGUE.items() if not font.is_bundled)
    return (
        PreviewSheet("fonts-everywhere.svg", everywhere, tuple(STYLES)),
        PreviewSheet("fonts-macos.svg", macos_only, ("standard",)),
        PreviewSheet("styles-macos.svg", MACOS_FAVOURITES, tuple(STYLES)),
    )


def write_preview_sheets(out_dir: Path, words: tuple[str, ...], lid: LidSpec) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    # A sheet needing fonts this computer lacks is skipped, not drawn half empty.
    for sheet in (sheet for sheet in preview_sheets() if sheet.can_be_drawn_here):
        path = out_dir / sheet.file_name
        write_svg(path, overview_svg(overview_rows(sheet.fonts, sheet.styles, words, lid), lid))
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
