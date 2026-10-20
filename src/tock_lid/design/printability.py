"""Finding spots in a layer too thin for the nozzle to print."""

from shapely.geometry.base import BaseGeometry

from tock_lid.design.layers import NOTICEABLE_SPOT_MM2, Layer


def largest_thin_spot_mm2(shape: BaseGeometry, min_line_mm: float) -> float:
    """The biggest piece that disappears when a min_line_mm wide brush is rolled through the shape."""
    if shape.is_empty:
        return 0.0
    radius = min_line_mm / 2
    thin = shape.difference(shape.buffer(-radius).buffer(radius))
    return max((piece.area for piece in getattr(thin, "geoms", [thin])), default=0.0)


def thin_layers(layers: list[Layer], min_line_mm: float) -> dict[str, float]:
    """Layer name to its largest thin spot, for the layers where that is more than a corner tip."""
    spots = {layer.name: largest_thin_spot_mm2(layer.shape, min_line_mm) for layer in layers}
    return {name: area for name, area in spots.items() if area > NOTICEABLE_SPOT_MM2}
