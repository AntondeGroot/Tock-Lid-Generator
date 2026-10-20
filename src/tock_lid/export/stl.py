"""Extruding a flat layer into a printable STL body."""

from pathlib import Path

import shapely
import trimesh
from shapely.geometry.base import BaseGeometry

# Specks smaller than this cannot be printed and only make the slicer complain.
MIN_PART_AREA_MM2 = 0.01
# STL stores 32-bit floats, about 4 µm apart near the lid edge. Vertices closer than that
# merge on load and leave a broken edge, so they are snapped to a coarser grid first.
STL_GRID_MM = 1e-4


def write_stl(path: Path, shape: BaseGeometry, thickness_mm: float) -> trimesh.Trimesh:
    mesh = extrude(shape, thickness_mm)
    mesh.export(path)
    return mesh


def extrude(shape: BaseGeometry, thickness_mm: float) -> trimesh.Trimesh:
    """The visible top face lies at z = 0 and the body goes down into the lid, to -thickness."""
    snapped = shapely.set_precision(shape, STL_GRID_MM)
    polygons = [p for p in getattr(snapped, "geoms", [snapped]) if p.area > MIN_PART_AREA_MM2]
    mesh = trimesh.util.concatenate([trimesh.creation.extrude_polygon(p, thickness_mm) for p in polygons])
    mesh.apply_translation((0, 0, -thickness_mm))
    return mesh
