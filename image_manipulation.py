from __future__ import annotations

from pathlib import Path
from typing import List

from PIL import ImageDraw
from PIL import ImageFilter
from PIL import Image
from PIL import ImageFont
from PIL import ImageOps

import exif
from area import NormalizedRectangle
from subprocess_util import execute_save


def open_image(src: Path | exif.ImageFiles, exif_rotation: bool = True) -> Image.Image:
    """
    Open image and rotate according to EXIF metadata.

    :param src:
    :param exif_rotation:
    :return:
    """
    if isinstance(src, exif.ImageFiles):
        src = src.get_image_file()

    # Open an image.
    image = Image.open(src)

    if exif_rotation:
        # Rotate according to EXIF orientation.
        image = ImageOps.exif_transpose(image)

    return image


def blur(image: Image.Image,
         areas: List[exif.ExifImageRegion | NormalizedRectangle]) -> Image.Image:
    """
    :param image:
    :param areas: Areas to blur on the given image.
    :return: Reference to the modified image.
    """
    if areas is None or len(areas) == 0:
        return image

    areas_ = []
    for area in areas:
        if isinstance(area, NormalizedRectangle):
            areas_.append(area)
        if isinstance(area, exif.ExifImageRegion):
            areas_.append(NormalizedRectangle.of_exif_image_region(area))
        else:
            raise Exception()
    areas = areas_

    # Create mask.
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)

    # For each rectangle: Draw a white rectangle to the mask.
    for area in areas:
        # Calculate top left and lower right corners of rectangle.
        im_width, im_height = image.size
        x1 = im_width * area.x
        y1 = im_height * area.y
        x2 = x1 + im_width * area.width
        y2 = y1 + im_height * area.height

        draw.rectangle(((x1, y1), (x2, y2)), fill=255)

    # Save the mask.
    mask_path = Path('mask.png')
    mask.save(mask_path)

    # Blur radius.
    # Between 50 and 250. Depending on how many pixels are inside the face-rectangle.
    # 50 for small faces on low-res images. 250 for a close-up on a high-resolution image.
    radius = 200
    # Blur image.
    blurred = image.filter(ImageFilter.GaussianBlur(radius))

    # Paste blurred region and save result.
    image.paste(blurred, mask=mask)

    mask_path.unlink(missing_ok=False)
    return image


def resize(image: Image.Image, max_resolution: int = 2048) -> Image.Image:
    if max_resolution is None or max_resolution < 0:
        return image

    actual_resolution: int = max(image.size[0], image.size[1])
    factor: float = max_resolution / actual_resolution
    return image.resize((round(factor * image.size[0]), round(factor * image.size[1])))


def add_text(image: Image.Image, text: str = None) -> Image.Image:
    if text is None or len(text) == 0:
        return image

    x = 80
    y = image.size[1] - 80

    font = ImageFont.truetype("/usr/share/fonts/noto/NotoSans-Regular.ttf", 64)
    d = ImageDraw.Draw(image)

    # anchor - Quick reference: https://pillow.readthedocs.io/en/stable/handbook/text-anchors.html#quick-reference
    anchor = 'ls'

    # Draw border around text
    d.text((x - 1, y - 1), text, anchor=anchor, font=font, fill="black")
    d.text((x + 1, y - 1), text, anchor=anchor, font=font, fill="black")
    d.text((x - 1, y + 1), text, anchor=anchor, font=font, fill="black")
    d.text((x + 1, y + 1), text, anchor=anchor, font=font, fill="black")
    # Draw text itself
    d.text((x, y), text, anchor=anchor, font=font, fill="white")

    return image


def save_image(image: Image.Image, dst: Path,
               src: Path | exif.ImageFiles = None,
               orientation: bool = True,
               gps: bool = True,
               date: bool = True
               ) -> Path:
    """
    Save image and copy some metadata from original image.

    :param image:
    :param dst:
    :param src:
    :param orientation:
    :param gps:
    :param date:
    :return:
    """
    # Save image.
    #
    # JPEG quality: https://jdhao.github.io/2019/07/20/pil_jpeg_image_quality/#other-options-for-quality
    # JPEG presets: https://github.com/python-pillow/Pillow/blob/main/src/PIL/JpegPresets.py#L67
    #   e.g. web_low, web_medium, web_high, web_very_high, web_maximum
    image.save(dst, format='jpeg', quality='web_low')

    if orientation or gps or date:
        copy_metadata(src, dst, orientation, gps, date)

    return dst


def copy_metadata(src: Path | exif.ImageFiles,
                  dst: Path,
                  orientation: bool = True,
                  gps: bool = True,
                  date: bool = True) -> None:
    if not (orientation or gps or date):
        return

    if isinstance(src, exif.ImageFiles):
        src = src.get_metadata_file()

    args = ['exiftool', '-overwrite_original', '-tagsfromfile', str(src)]
    if orientation:
        args += ['-orientation']
    if gps:
        args += ['-gps:all']
    if date:
        args += ['-alldates']
    args += [str(dst)]

    print(f'  Copying metadata ...')
    execute_save(args)
