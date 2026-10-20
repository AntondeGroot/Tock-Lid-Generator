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
# Larger loose pieces are left alone: checking them is slow and any thin part gets reported.
LARGEST_SLIVER_DOTS = 8
# Every sharp corner leaves a tip of at most ~0.06 mm² that the check cannot tell apart from
# a real problem; a needle or strip the printer would actually botch is several times larger.
NOTICEABLE_SPOT_MM2 = 0.1
BORDER_TOLERANCE_MM = 1e-4  # how close two edges must be to count as a shared border


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
    # Strips of background in tight pockets cannot be printed; the outermost ring takes them.
    strips = _narrow_parts(background, lid)
    outermost = replace(outermost, shape=outermost.shape.union(strips))
    background_layer = Layer(BACKGROUND, background.difference(strips), style.background_colour)
    return _without_unprintable_islands([*inner_layers, outermost, background_layer], lid)


def _narrow_parts(shape: BaseGeometry, lid: LidSpec) -> BaseGeometry:
    """Parts narrower than a printable line.

    Only these spots change; the rest of the boundary keeps its points, so files stay small."""
    radius = lid.min_line_mm / 2
    narrow = shape.difference(shape.buffer(-radius).buffer(radius))
    return unary_union([piece for piece in _pieces(narrow) if piece.area > NUMERICAL_NOISE_MM2])


def _without_unprintable_islands(layers: list[Layer], lid: LidSpec) -> list[Layer]:
    """Hands every loose piece too small or thin to print to the layer that surrounds it most."""
    shapes = [layer.shape for layer in layers]
    for index in range(len(shapes)):
        for island in _unprintable_islands(shapes[index], lid):
            others = [other for other in range(len(shapes)) if other != index]
            neighbour = max(others, key=lambda other: _shared_border_mm(island, shapes[other]))
            shapes[index] = shapes[index].difference(island)
            shapes[neighbour] = shapes[neighbour].union(island)
    return [replace(layer, shape=shape) for layer, shape in zip(layers, shapes, strict=True)]


def _unprintable_islands(shape: BaseGeometry, lid: LidSpec) -> list[BaseGeometry]:
    """Loose pieces that are too small to print, or that the thin-spot check would flag.

    Too small: the printable core is under a dot two nozzle widths across. Too thin: more
    than a corner tip of it is narrower than one line, as in a sliver trapped in a pocket."""
    smallest_dot_mm2 = math.pi * lid.min_line_mm**2
    candidates = [piece for piece in _pieces(shape) if piece.area < LARGEST_SLIVER_DOTS * smallest_dot_mm2]
    return [piece for piece in candidates if _is_unprintable(piece, smallest_dot_mm2, lid)]


def _is_unprintable(piece: BaseGeometry, smallest_dot_mm2: float, lid: LidSpec) -> bool:
    core_mm2 = _printable_core(piece, lid).area
    return core_mm2 < smallest_dot_mm2 or piece.area - core_mm2 > NOTICEABLE_SPOT_MM2


def _printable_core(shape: BaseGeometry, lid: LidSpec) -> BaseGeometry:
    radius = lid.min_line_mm / 2
    return shape.buffer(-radius).buffer(radius)


def _shared_border_mm(island: BaseGeometry, shape: BaseGeometry) -> float:
    return shape.boundary.intersection(island.buffer(BORDER_TOLERANCE_MM)).length


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
