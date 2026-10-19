"""Turning a word outline into the coloured layers of a lid insert."""

from tock_lid.design.fitting import fit_scale
from tock_lid.design.layers import Layer, lid_layers
from tock_lid.design.lid import LidSpec
from tock_lid.design.printability import thin_layers
from tock_lid.design.styles import STYLES, Ring, Style, find_style

__all__ = [
    "STYLES",
    "Layer",
    "LidSpec",
    "Ring",
    "Style",
    "find_style",
    "fit_scale",
    "lid_layers",
    "thin_layers",
]
