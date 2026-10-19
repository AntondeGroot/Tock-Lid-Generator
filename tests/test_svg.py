import re

from shapely.geometry import box

from tock_lid.export.svg import path_data


def test_shapes_above_the_lid_centre_stay_above_it_in_the_svg():
    # Geometry is y-up, SVG is y-down: a box 10-11 mm above the centre must get SVG y -11..-10.
    above_centre = box(0, 10, 1, 11)

    data = path_data(above_centre)

    numbers = [float(n) for n in re.findall(r"-?\d+\.\d+", data)]
    svg_ys = numbers[1::2]
    assert min(svg_ys) == -11.0
    assert max(svg_ys) == -10.0
