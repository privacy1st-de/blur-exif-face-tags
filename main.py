import os
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
    # Convert all images in the image_directory, including subdirectories.
    for _, _, files in os.walk(image_directory):
        for relative_file_str in files:
            file: Path = Path.joinpath(image_directory, relative_file_str)
            if file.suffix.lower() in image_extensions:

                if file.stem.endswith(blur.stem_suffix()):
                    print(f'Skipped the following image as it is already blurred:\n\t{file}')
                elif blur.get_image_dst(file).exists():
                    print(f'Skipped the following image as it\'s blurred output does already exist:\n\t{file}')
                else:
                    blur_image(exif.Image(file))


if __name__ == '__main__':
    main()
