from __future__ import annotations

import exif


class NormalizedRectangle:
    """
    x, y, width and height are normalized: Their values are in the range [0, 1].
    """

    x: float
    y: float
    width: float
    height: float

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    @staticmethod
    def of_exif_image_region(region: exif.ExifImageRegion) -> NormalizedRectangle:
        if region.area_unit == 'normalized':
            return NormalizedRectangle(
                x=region.rectangle[0],
                y=region.rectangle[1],
                width=region.rectangle[2],
                height=region.rectangle[3]
            )
        else:
            raise Exception()
