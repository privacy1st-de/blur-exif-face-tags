import os
from pathlib import Path

import exif
import image_manipulation
from exif import ExifImageRegion, get_exif_image_regions

# ======================================================================================================= #

image_directory = Path('example')  # Image directory.

names = ['A', 'B', 'C']  # Names of Persons to be blurred.
# names = []  # Blurr all faces.

resolution = 2048  # Resize image.
# resolution = None  # Keep original image size.
text = "Example"  # Add text to image.
# text = None  # Do not add text.

copy_metadata_orientation: bool = False  # Copies orientation metadata from original image.
copy_metadata_gps: bool = True  # Copies gps location metadata from original image.
copy_metadata_date: bool = True  # Copies date metadata from original image.

# List of lower-case image extensions.
image_extensions = ['.jpg', '.jpeg', '.png']


# ======================================================================================================= #

def main():
    # Convert all images in `image_directory`, including subdirectories.
    for _, _, files in os.walk(image_directory):
        for relative_file_str in files:
            file: Path = Path.joinpath(image_directory, relative_file_str)
            if file.suffix.lower() not in image_extensions:
                continue
            if stem_suffix() in file.stem:
                print(f'Skipped the following image as it is already blurred:\n\t{file}')
                continue
            dst = get_image_dst(file)
            if dst.exists():
                # Blur again as the source image might have different face tags now.
                dst.unlink()

            print(f'{file}')
            blur_image(exif.ImageFiles(file), dst)


def blur_image(image_files: exif.ImageFiles, dst: Path) -> Path:
    """
    If at least one tagged area of the image matches the criteria,
    a blurred image is created and its path is returned.
    """
    exif_image_regions: list[ExifImageRegion] = get_exif_image_regions(image=image_files)

    # Blur only some faces.
    areas = []
    r_types = ['Face']
    for region in exif_image_regions:
        if len(r_types) > 0 and region.r_type not in r_types:
            continue
        if region.name in names or len(names) == 0:
            areas.append(region)

    print(f'  Blurring {len(areas)} areas ...')

    im = image_manipulation.open_image(image_files)
    im = image_manipulation.blur(im, areas)
    im = image_manipulation.resize(im, resolution)
    im = image_manipulation.add_text(im, text)
    return image_manipulation.save_image(im, dst, image_files)


def get_image_dst(image: Path) -> Path:
    return image.parent.joinpath(f'{image.stem}{stem_suffix()}{image.suffix}')


def stem_suffix() -> str:
    """
    Modified images will be saved with a different filename.
    This suffix will be added to their stem.
    """
    return '[blurred]'


if __name__ == '__main__':
    main()
