"""SVG documents in millimetres, centred on the lid so every file lines up on import."""

from pathlib import Path

from shapely.geometry.base import BaseGeometry

from tock_lid.design.layers import Layer
from tock_lid.design.lid import LidSpec

CANVAS_PADDING_MM = 4.0
PRINT_DECIMALS = 3  # micrometres, well below what CAD or a printer resolves
GUIDE_STYLE = 'fill="none" stroke="#999" stroke-width="0.3" stroke-dasharray="2 1.5"'


def lid_svg(layers: list[Layer], lid: LidSpec, guide: bool = False) -> str:
    """A standalone document; the dashed guide circle shows the lid edge in previews."""
    half = lid.radius_mm + CANVAS_PADDING_MM
    guide_circle = f'  <circle r="{lid.radius_mm}" {GUIDE_STYLE}/>\n' if guide else ""
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{2 * half}mm" height="{2 * half}mm" '
        f'viewBox="{-half} {-half} {2 * half} {2 * half}">\n'
        f"{guide_circle}{layer_paths(layers)}</svg>\n"
    )


def write_svg(path: Path, document: str) -> None:
    """UTF-8 with Unix line endings, so a file is byte-identical on Windows, macOS and Linux."""
    path.write_text(document, encoding="utf-8", newline="\n")


def layer_paths(layers: list[Layer], decimals: int = PRINT_DECIMALS) -> str:
    return "".join(_layer_path(layer, decimals) for layer in layers)


def _layer_path(layer: Layer, decimals: int) -> str:
    data = path_data(layer.shape, decimals)
    return f'  <path id="{layer.name}" fill="{layer.colour}" fill-rule="evenodd" d="{data}"/>\n'


def path_data(shape: BaseGeometry, decimals: int = PRINT_DECIMALS) -> str:
    """SVG has y pointing down, so y is negated to keep the text upright."""
    polygons = getattr(shape, "geoms", [shape])
    rings = [ring for polygon in polygons for ring in (polygon.exterior, *polygon.interiors)]
    return " ".join(_ring_data(ring.coords, decimals) for ring in rings)


def _ring_data(coords, decimals: int) -> str:
    return "M" + " L".join(f"{x:.{decimals}f} {-y:.{decimals}f}" for x, y in coords) + " Z"
