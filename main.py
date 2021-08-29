from pathlib import Path
from typing import List

import exif, blur

from exif import ExifImageRegion, get_exif_image_regions

image_extensions = ['.jpg', '.jpeg', '.png']
image_directory = Path('example/')  # TODO: Adjust path to folder with images

r_type = 'Face'
names = ['A', 'B', 'C']  # TODO: Enter name of persons to be blurred


def blur_image(image: exif.Image):
    exif_image_regions: List[ExifImageRegion] = get_exif_image_regions(image=image)

    # Blur all tagged areas
    # normalized_rectangles = [blur.NormalizedRectangle.of_exif_image_region(region) for region in exif_image_regions]

    # Blur only some faces
    normalized_rectangles = []
    for region in exif_image_regions:
        if region.r_type == r_type and region.name in names:
            normalized_rectangles += [blur.NormalizedRectangle.of_exif_image_region(region)]
    print(f'{image} contains {len(normalized_rectangles)} tagged faces to be blurred!')

    blur.blur_rectangle1(image_src=image, normalized_rectangles=normalized_rectangles)


def main():
    for child in image_directory.iterdir():
        if child.suffix.lower() in image_extensions:
            blur_image(exif.Image(child))


if __name__ == '__main__':
    main()
