import os
from pathlib import Path
from typing import List, Union

import blur
import exec
import exif
from exif import ExifImageRegion, get_exif_image_regions

# ======================================================================================================= #

# Adjust path to folder with images
image_directory = Path('example')

# Enter name of persons to be blurred. Leave empty to blur any face.
names = ['A', 'B', 'C']
# names = []

delete_original: bool = True  # deletes the original image after blurring image was created
copy_metadata_gps: bool = True  # copies gps location from original to blurred image
copy_metadata_date: bool = True  # copies date from original to blurred image

# Lower-case image extensions.
image_extensions = ['.jpg', '.jpeg', '.png']

r_types = ['Face']

# ======================================================================================================= #


def blur_image(image: exif.Image) -> Union[Path, None]:
    """
    If at least one tagged area of the image matches the criteria,
    a blurred image is created and its path is returned.
    """
    exif_image_regions: List[ExifImageRegion] = get_exif_image_regions(image=image)

    # Blur only some faces.
    normalized_rectangles = []
    for region in exif_image_regions:
        if len(r_types) > 0 and region.r_type not in r_types:
            continue
        if region.name in names or len(names) == 0:
            normalized_rectangles += [blur.NormalizedRectangle.of_exif_image_region(region)]

    if len(normalized_rectangles) > 0:
        print(f'  Blurring {len(normalized_rectangles)} areas ...')
        return blur.blur_rectangle1(image_src=image, normalized_rectangles=normalized_rectangles)
    else:
        return None


def main():
    # Convert all images in `image_directory`, including subdirectories.
    for _, _, files in os.walk(image_directory):
        for relative_file_str in files:
            file: Path = Path.joinpath(image_directory, relative_file_str)
            if file.suffix.lower() not in image_extensions:
                continue
            if file.stem.endswith(blur.stem_suffix()):
                print(f'Skipped the following image as it is already blurred:\n\t{file}')
                continue
            if blur.get_image_dst(file).exists():
                print(f'Skipped the following image as it\'s blurred output does already exist:\n\t{file}')
                continue

            print(f'{file}')
            blurred_img = blur_image(exif.Image(file))

            if blurred_img is not None and copy_metadata_gps:
                print(f'  Copying gps metadata to blurred file ...')
                exec.execute_save(['exiftool', '-tagsfromfile', str(file), '-gps:all', str(blurred_img)])
            if blurred_img is not None and copy_metadata_date:
                print(f'  Copying date metadata to blurred file ...')
                exec.execute_save(['exiftool', '-tagsfromfile', str(file), '-alldates', str(blurred_img)])
            if blurred_img is not None and delete_original:
                print(f'  Deleting original file ...')
                file.unlink()


if __name__ == '__main__':
    main()
