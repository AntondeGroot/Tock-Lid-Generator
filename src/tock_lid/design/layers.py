"""Building the coloured layers: letter fill, outline rings, and the background disc.

All shapes are in millimetres, y up, centred on the middle of the lid."""

import math
from dataclasses import dataclass, replace

from shapely import affinity
from shapely.geometry import Point
from shapely.geometry.base import BaseGeometry
from shapely.ops import unary_union

from tock_lid.design.lid import LidSpec
from tock_lid.design.styles import Style

FILL = "fill"
BACKGROUND = "background"
DISC_QUARTER_SEGMENTS = 128
NUMERICAL_NOISE_MM2 = 1e-3  # slivers from regrowing curves as polygons, not real features


@dataclass(frozen=True)
class Layer:
    name: str
    shape: BaseGeometry
    colour: str


def text_layers(outline: BaseGeometry, scale: float, style: Style, lid: LidSpec) -> list[Layer]:
    """The fill first, then each ring outward. Together they tile the text area exactly."""
    letters = _centred(affinity.scale(outline, scale, scale, origin=(0, 0)))
    fill = _grow_without_slivers(letters, lid.fatten_mm, lid)
    layers = [Layer(FILL, fill, style.fill_colour)]
    inner = fill
    for ring in style.rings:
        outer = _grow_without_slivers(inner, ring.width_mm, lid)
        layers.append(Layer(ring.name, outer.difference(inner), ring.colour))
        inner = outer
    return layers


def lid_layers(outline: BaseGeometry, scale: float, style: Style, lid: LidSpec) -> list[Layer]:
    """The text layers plus the rest of the disc, so every part of the lid has one colour."""
    *inner_layers, outermost = text_layers(outline, scale, style, lid)
    disc = Point(0, 0).buffer(lid.radius_mm, quad_segs=DISC_QUARTER_SEGMENTS)
    background = disc.difference(unary_union([layer.shape for layer in [*inner_layers, outermost]]))
    # Specks of background left in tiny pockets cannot be printed; the outermost ring takes them.
    specks = _unprintable_specks(background, lid)
    outermost = replace(outermost, shape=outermost.shape.union(specks))
    background_layer = Layer(BACKGROUND, background.difference(specks), style.background_colour)
    return [*inner_layers, outermost, background_layer]


def _unprintable_specks(shape: BaseGeometry, lid: LidSpec) -> BaseGeometry:
    """Parts narrower than a printable line, plus the islands that cutting those off leaves behind.

    Only these spots change; the rest of the boundary keeps its points, so files stay small."""
    radius = lid.min_line_mm / 2
    narrow = shape.difference(shape.buffer(-radius).buffer(radius))
    narrow = unary_union([piece for piece in _pieces(narrow) if piece.area > NUMERICAL_NOISE_MM2])
    smallest_dot_mm2 = math.pi * lid.min_line_mm**2  # a dot two nozzle widths across
    islands = [piece for piece in _pieces(shape.difference(narrow)) if piece.area < smallest_dot_mm2]
    return unary_union([narrow, *islands])


def _pieces(shape: BaseGeometry) -> list[BaseGeometry]:
    return list(getattr(shape, "geoms", [shape]))


def _centred(shape: BaseGeometry) -> BaseGeometry:
    min_x, min_y, max_x, max_y = shape.bounds
    return affinity.translate(shape, -(min_x + max_x) / 2, -(min_y + max_y) / 2)


def _grow_without_slivers(shape: BaseGeometry, width_mm: float, lid: LidSpec) -> BaseGeometry:
    """Grows the shape, then closes pockets narrower than a printable line.

    Without the closing, the next ring outward would get unprintable slivers: needles in
    the sharp notch where two strokes of a letter meet, and strips where two letters'
    outlines almost meet."""
    closing = lid.min_line_mm / 2
    grown = shape.buffer(width_mm + closing, join_style="round").buffer(-closing)
    return grown.simplify(lid.simplify_mm)
