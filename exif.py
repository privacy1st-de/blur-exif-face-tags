from pathlib import Path
from image_files import ImageFiles
from subprocess_util import execute_save


class ExifImageRegion:
    """
    A rectangular region of an image.
    For example a face tag.
    """

    image_files: ImageFiles

    name: str  # 'John'
    r_type: str  # 'Face'
    area_unit: str  # 'normalized'
    rectangle: list[float]  # [ x-coordinate, y-coordinate, width, height ]

    def __init__(self, image_files: ImageFiles, name, r_type, area_unit, rectangle):
        self.image_files = image_files
        self.name = name
        self.r_type = r_type
        self.area_unit = area_unit
        self.rectangle = rectangle

    def __str__(self):
        return f'ExifImageRegion: {self.__dict__}'


def get_exif_image_regions(image: ImageFiles) -> list[ExifImageRegion]:
    img_metadata_file: Path = image.get_metadata_file()

    names_str = execute_save(['exiftool', '-RegionName', str(img_metadata_file)])
    r_types_str = execute_save(['exiftool', '-RegionType', str(img_metadata_file)])
    area_units_str = execute_save(['exiftool', '-RegionAreaUnit', str(img_metadata_file)])
    rectangles_str = execute_save(['exiftool', '-RegionRectangle', str(img_metadata_file)])

    if len(names_str) == len(r_types_str) == len(area_units_str) == len(rectangles_str) == 0:
        # there are no tagged areas on this image
        return []

    names = names_str.strip().split(':', 1)[1].strip().split(', ')
    r_types = r_types_str.strip().split(':', 1)[1].strip().split(', ')
    area_units = area_units_str.strip().split(':', 1)[1].strip().split(', ')
    rectangles_tmp = rectangles_str.strip().split(':', 1)[1].strip().split(', ')

    assert len(rectangles_tmp) % 4 == 0
    rectangles = []
    for i in range(len(rectangles_tmp) // 4):
        rectangles += [[]]
        for j in range(4):
            rectangles[i] += [None]
            rectangles[i][j] = float(rectangles_tmp[i * 4 + j])

    return [ExifImageRegion(image_files=image, name=name, r_type=r_type, area_unit=area_unit, rectangle=rectangle) for
            name, r_type, area_unit, rectangle in zip(names, r_types, area_units, rectangles)]
