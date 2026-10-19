"""One sheet comparing fonts and styles: a row per design, a lid per word."""

from dataclasses import dataclass, replace

from tock_lid.design.layers import Layer
from tock_lid.design.lid import LidSpec
from tock_lid.export.svg import layer_paths

CELL_PADDING_MM = 4.0
DISPLAY_TOLERANCE_MM = 0.1
DISPLAY_DECIMALS = 1
TITLE_HEIGHT_MM = 10.0
TITLE_STYLE = 'font-family="Helvetica" font-size="6" fill="#444"'
LID_EDGE_STYLE = 'fill="none" stroke="#888" stroke-width="0.4"'


@dataclass(frozen=True)
class OverviewRow:
    title: str
    lids: list[list[Layer]]


def overview_svg(rows: list[OverviewRow], lid: LidSpec) -> str:
    cell = lid.diameter_mm + 2 * CELL_PADDING_MM
    row_height = cell + TITLE_HEIGHT_MM
    width = cell * max(len(row.lids) for row in rows)
    height = row_height * len(rows)
    body = "\n".join(_row(row, index * row_height, cell, lid) for index, row in enumerate(rows))
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}mm" height="{height}mm" '
        f'viewBox="0 0 {width} {height}">\n<rect width="100%" height="100%" fill="#fff"/>\n{body}\n</svg>\n'
    )


def _row(row: OverviewRow, top: float, cell: float, lid: LidSpec) -> str:
    title = f'<text x="2" y="{top + 7}" {TITLE_STYLE}>{row.title}</text>'
    centre_y = top + TITLE_HEIGHT_MM + cell / 2
    lids = [_lid(layers, column * cell + cell / 2, centre_y, lid) for column, layers in enumerate(row.lids)]
    return "\n".join([title, *lids])


def _lid(layers: list[Layer], centre_x: float, centre_y: float, lid: LidSpec) -> str:
    edge = f'<circle r="{lid.radius_mm}" {LID_EDGE_STYLE}/>'
    paths = layer_paths([_for_display(layer) for layer in layers], DISPLAY_DECIMALS)
    return f'<g transform="translate({centre_x} {centre_y})">{paths}{edge}</g>'


def _for_display(layer: Layer) -> Layer:
    """A sheet is looked at, not printed, so it can drop detail and stay small."""
    return replace(layer, shape=layer.shape.simplify(DISPLAY_TOLERANCE_MM))
