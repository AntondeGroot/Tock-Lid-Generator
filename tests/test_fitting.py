from shapely.geometry import box

from tock_lid.design import STYLES, LidSpec, fit_scale
from tock_lid.design.fitting import furthest_point_mm
from tock_lid.design.layers import text_layers

LID = LidSpec()
FIT_TOLERANCE_MM = 0.01


def test_outlined_text_just_touches_the_margin_circle():
    # A wide "word" in the thick style: its 1.6 mm outline must count towards the fit.
    outline = box(0, 0, 400, 100)
    style = STYLES["thick"]

    scale = fit_scale(outline, style, LID)

    outermost_ring = text_layers(outline, scale, style, LID)[-1].shape
    reach = furthest_point_mm(outermost_ring)
    assert LID.text_radius_mm - FIT_TOLERANCE_MM <= reach <= LID.text_radius_mm
