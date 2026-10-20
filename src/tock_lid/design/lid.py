"""Physical dimensions of the lid insert and the printer's limits, in millimetres."""

from dataclasses import dataclass


@dataclass(frozen=True)
class LidSpec:
    diameter_mm: float = 122.4
    margin_mm: float = 5.0  # clearance between the text and the edge of the disc
    thickness_mm: float = 0.8
    min_line_mm: float = 0.4  # narrowest line the nozzle prints reliably
    fatten_mm: float = 0.2  # thickens hairlines so thin strokes still get a coloured fill
    simplify_mm: float = 0.02  # far below print resolution; keeps files small

    @property
    def radius_mm(self) -> float:
        return self.diameter_mm / 2

    @property
    def text_radius_mm(self) -> float:
        return self.radius_mm - self.margin_mm
