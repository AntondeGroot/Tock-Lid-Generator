"""Choosing the letter size so the outlined text just fits inside the lid's margin."""

from shapely.geometry.base import BaseGeometry

from tock_lid.design.layers import text_layers
from tock_lid.design.lid import LidSpec
from tock_lid.design.styles import Style

SEARCH_STEPS = 30


def fit_scale(outline: BaseGeometry, style: Style, lid: LidSpec) -> float:
    """Font units to millimetres, found by bisection because the rings do not scale with the text."""
    too_small, too_large = 0.0, _scale_without_rings(outline, lid)
    for _ in range(SEARCH_STEPS):
        scale = (too_small + too_large) / 2
        if _reach_mm(outline, scale, style, lid) <= lid.text_radius_mm:
            too_small = scale
        else:
            too_large = scale
    if too_small == 0.0:
        raise ValueError(f"The '{style.name}' outline alone is wider than the {lid.diameter_mm} mm lid.")
    return too_small


def furthest_point_mm(shape: BaseGeometry) -> float:
    """Distance from the lid centre to the furthest point of the shape."""
    polygons = getattr(shape, "geoms", [shape])
    return max((x * x + y * y) ** 0.5 for polygon in polygons for x, y in polygon.exterior.coords)


def _scale_without_rings(outline: BaseGeometry, lid: LidSpec) -> float:
    """An upper bound: the bare letters' half-diagonal touching the margin circle."""
    min_x, min_y, max_x, max_y = outline.bounds
    half_diagonal = ((max_x - min_x) ** 2 + (max_y - min_y) ** 2) ** 0.5 / 2
    return lid.text_radius_mm / half_diagonal


def _reach_mm(outline: BaseGeometry, scale: float, style: Style, lid: LidSpec) -> float:
    outermost = text_layers(outline, scale, style, lid)[-1].shape
    return furthest_point_mm(outermost)
