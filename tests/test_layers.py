import pytest
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from tock_lid.design import STYLES, LidSpec, lid_layers, thin_layers

LID = LidSpec()


def test_layers_tile_the_disc_without_gaps_or_overlaps():
    # Two "letters" 0.3 mm apart: a pocket narrower than one printable line.
    outline = unary_union([box(0, 0, 10, 20), box(10.3, 0, 20, 20)])

    layers = lid_layers(outline, scale=2.0, style=STYLES["double"], lid=LID)

    disc_area = Point(0, 0).buffer(LID.radius_mm, quad_segs=128).area
    overlap = sum(a.shape.intersection(b.shape).area for i, a in enumerate(layers) for b in layers[i + 1 :])
    assert overlap < 1e-6
    assert sum(layer.shape.area for layer in layers) == pytest.approx(disc_area, rel=1e-9)


def test_no_layer_gets_slivers_where_two_letters_nearly_touch():
    # 1.1 units x scale 2 = 2.2 mm apart; after the 0.2 mm fattening and the 0.8 mm inner
    # outline on both letters, only 0.2 mm would be left for the gap ring.
    outline = unary_union([box(0, 0, 10, 20), box(11.1, 0, 21.1, 20)])

    layers = lid_layers(outline, scale=2.0, style=STYLES["double"], lid=LID)

    assert thin_layers(layers, LID.min_line_mm) == {}


def test_outline_does_not_end_in_a_needle_where_two_strokes_meet():
    # Three prongs, like a "W" with a middle stroke: between them are two notches that taper
    # to a sharp point at y = 8, the way strokes meet in the crotch of an "n" or a "K".
    three_prongs = Polygon(
        [(0, 0), (6, 0), (12, 30), (8, 30), (3.5, 8), (4, 30), (2, 30), (2.5, 8), (-2, 30), (-6, 30)]
    )

    layers = lid_layers(three_prongs, scale=1.0, style=STYLES["standard"], lid=LID)

    assert thin_layers(layers, LID.min_line_mm) == {}


def test_a_letter_hole_too_small_for_background_is_filled_by_the_outline():
    # A 2.6 mm hole: after 0.2 mm fattening and the 0.8 mm outline on all sides, only a
    # 0.6 mm dot of background would be left inside it, too small to print.
    letter_with_hole = box(-10, -10, 10, 10).difference(Point(0, 0).buffer(1.3))

    *_, outline, background = lid_layers(letter_with_hole, scale=1.0, style=STYLES["standard"], lid=LID)

    assert outline.shape.contains(Point(0, 0))
    assert background.shape.geom_type == "Polygon"
