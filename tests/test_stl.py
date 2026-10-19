import pytest
import trimesh
from shapely.geometry import MultiPolygon, Point, Polygon, box

from tock_lid.export import write_stl


def test_written_stl_is_watertight_and_as_thick_as_requested(tmp_path):
    # Two separate parts, one with a hole, like the letters "l" and "o".
    letter_o = Point(30, 0).buffer(10).difference(Point(30, 0).buffer(4))
    shape = MultiPolygon([box(0, -10, 5, 10), letter_o])
    path = tmp_path / "letters.stl"

    write_stl(path, shape, thickness_mm=1.2)

    mesh = trimesh.load(path)
    (_, _, bottom), (_, _, top) = mesh.bounds
    assert mesh.is_watertight
    assert (bottom, top) == pytest.approx((0.0, 1.2))
    assert mesh.volume == pytest.approx(shape.area * 1.2, rel=1e-6)


def test_stl_stays_watertight_when_two_corners_are_closer_than_stl_precision(tmp_path):
    # STL stores 32-bit floats, ~4 µm apart at x = 50 mm: these two corners 0.3 µm apart
    # would merge into one point on load and break the mesh unless snapped first.
    near_duplicate_corner = Polygon([(50, 0), (56, 0), (56, 6), (50.0000003, 6.0000002), (50, 6)])
    path = tmp_path / "edge.stl"

    write_stl(path, near_duplicate_corner, thickness_mm=1.0)

    assert trimesh.load(path).is_watertight
