"""Flattening one glyph into a shapely polygon (font units, y up)."""

import pathops
from fontTools.pens.basePen import BasePen
from shapely.geometry import Polygon
from shapely.geometry.base import BaseGeometry

CURVE_STEPS = 16

Point = tuple[float, float]


def glyph_outline(glyph, glyph_set) -> BaseGeometry:
    """Overlapping contours are merged first, so even-odd filling is exact."""
    path = pathops.Path()
    glyph.draw(path.getPen(glyphSet=glyph_set))
    path.simplify(fix_winding=True)
    pen = _FlatteningPen(glyph_set)
    path.draw(pen)
    outline = Polygon()
    for contour in pen.contours:
        outline = outline.symmetric_difference(Polygon(contour).buffer(0))
    return outline


class _FlatteningPen(BasePen):
    """Collects every contour as a list of points, with curves sampled into line segments."""

    def __init__(self, glyph_set):
        super().__init__(glyph_set)
        self.contours: list[list[Point]] = []
        self._current: list[Point] = []

    def _moveTo(self, pt):  # noqa: N802 - fontTools pen protocol
        self._current = [pt]

    def _lineTo(self, pt):  # noqa: N802
        self._current.append(pt)

    def _curveToOne(self, pt1, pt2, pt3):  # noqa: N802
        self._sample_curve((self._getCurrentPoint(), pt1, pt2, pt3))

    def _qCurveToOne(self, pt1, pt2):  # noqa: N802
        self._sample_curve((self._getCurrentPoint(), pt1, pt2))

    def _closePath(self):  # noqa: N802
        if len(self._current) >= 3:
            self.contours.append(self._current)
        self._current = []

    _endPath = _closePath  # noqa: N815 - fontTools pen protocol

    def _sample_curve(self, control_points: tuple[Point, ...]):
        for step in range(1, CURVE_STEPS + 1):
            self._current.append(_bezier_point(control_points, step / CURVE_STEPS))


def _bezier_point(control_points: tuple[Point, ...], t: float) -> Point:
    """De Casteljau evaluation; works for quadratic and cubic curves alike."""
    points = list(control_points)
    while len(points) > 1:
        points = [
            ((1 - t) * x0 + t * x1, (1 - t) * y0 + t * y1)
            for (x0, y0), (x1, y1) in zip(points, points[1:], strict=False)
        ]
    return points[0]
