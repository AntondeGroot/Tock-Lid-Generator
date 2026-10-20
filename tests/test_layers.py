import pytest
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union

from tock_lid.design import STYLES, LidSpec, lid_layers, thin_layers
from tock_lid.design.layers import Layer, _without_unprintable_islands

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


def test_a_dot_too_small_to_print_joins_the_layer_that_surrounds_it():
    dot = Point(5, 5).buffer(0.3)  # 0.6 mm across, below the 0.8 mm printable dot
    inner_ring = Layer("outline-inner", box(0, 0, 10, 10).difference(dot), "#000")
    gap = Layer("gap", unary_union([box(20, 0, 30, 10), dot]), "#fff")
    outer_ring = Layer("outline-outer", box(10, 0, 20, 10), "#000")  # next door, but not around the dot

    inner_ring, gap, outer_ring = _without_unprintable_islands([inner_ring, gap, outer_ring], LID)

    assert inner_ring.shape.contains(Point(5, 5))
    assert gap.shape.geom_type == "Polygon"
    assert outer_ring.shape.area == pytest.approx(100)


def test_a_thin_sliver_joins_the_layer_that_surrounds_it_even_if_its_core_could_print():
    # 6 mm long, tapering from 0.7 mm wide to a point: the wide end could print on its own,
    # but its tapering third (about 0.65 mm²) is narrower than one 0.4 mm line.
    sliver = Polygon([(2, 0), (8, 0.35), (8, -0.35)])
    inner_ring = Layer("outline-inner", box(0, -5, 10, 5).difference(sliver), "#000")
    gap = Layer("gap", unary_union([box(20, -5, 30, 5), sliver]), "#fff")
    outer_ring = Layer("outline-outer", box(10, -5, 20, 5), "#000")

    inner_ring, gap, _ = _without_unprintable_islands([inner_ring, gap, outer_ring], LID)

    assert inner_ring.shape.contains(Point(6, 0))
    assert gap.shape.geom_type == "Polygon"
