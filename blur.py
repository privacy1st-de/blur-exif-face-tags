from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import ImageDraw
from PIL import ImageFilter
from PIL import Image

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
            return NormalizedRectangle(x=region.rectangle[0], y=region.rectangle[1],
                                       width=region.rectangle[2], height=region.rectangle[3])
        else:
            raise Exception


def blur_rectangle0(image_src: exif.Image, region: exif.ExifImageRegion, image_dst: Path = None):
    if region.area_unit == 'normalized':
        blur_rectangle1(image_src, normalized_rectangles=[NormalizedRectangle.of_exif_image_region(region=region)],
                        image_dst=image_dst)
    else:
        raise Exception


def blur_rectangle1(image_src: exif.Image, normalized_rectangles: List[NormalizedRectangle], image_dst: Path = None):
    blur_rectangle2(image_src.get_image_file(), normalized_rectangles,
                    image_dst=image_dst)


def blur_rectangle2(image_src: Path, normalized_rectangles: List[NormalizedRectangle], image_dst: Path = None):
    if len(normalized_rectangles) == 0:
        print('No rectangles to blur')
        return

    # Open an image
    im = Image.open(image_src)

    # Create mask
    mask = Image.new('L', im.size, 0)
    draw = ImageDraw.Draw(mask)

    # For each rectangle: Draw a white rectangle to the mask
    for normalized_rectangle in normalized_rectangles:
        # Calculate top left and lower right corners of rectangle
        im_width, im_height = im.size
        x1 = im_width * normalized_rectangle.x
        y1 = im_height * normalized_rectangle.y
        x2 = x1 + im_width * normalized_rectangle.width
        y2 = y1 + im_height * normalized_rectangle.height

        draw.rectangle([(x1, y1), (x2, y2)], fill=255)

    # Save the mask
    mask.save('mask.png')

    # Blur image
    blurred = im.filter(ImageFilter.GaussianBlur(52))

    # Paste blurred region and save result
    im.paste(blurred, mask=mask)

    # Save image
    if image_dst is None:
        image_dst = get_image_dst(image_src)
    im.save(image_dst)


def get_image_dst(image: Path):
    return image.parent.joinpath(f'{image.stem}{stem_suffix()}{image.suffix}')


def stem_suffix():
    """
    Modified images will be saved with a different filename.
    This suffix will be added to their stem.
    """

    # return ' [blurred]'
    return '_blurred'
