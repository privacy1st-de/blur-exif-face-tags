from pathlib import Path
from typing import List, AnyStr
import exec


class Image:
    """
    An image may be just a single file (e.g. "IMG_001.RAF") or
    multiple files ("IMG_002.JPG" (image-data) and
    "IMG_002.JPG.xmp" (additional metadata)).
    """

    files: List[Path]

    def __init__(self, image_file: Path):
        if image_file.is_file():
            self.files = [image_file]
            image_file_name = image_file.name  # file.name ==> file basename
            for sibling in image_file.parent.iterdir():
                sibling_stem = sibling.stem  # file.stem ==> file basename without extension
                if sibling_stem == image_file_name:
                    self.files += [sibling]
            if len(self.files) == 0:
                raise Exception
        else:
            raise Exception

    def get_image_file(self):
        return self.files[0]

    def get_xmp_metadata(self) -> AnyStr:
        # TODO: Try to read xmp metadata from the image file itself, if there is no sidecar xmp file

        xmp_sidecar = self.get_xmp_sidecar()
        with open(xmp_sidecar, "r") as f:
            return f.read()

    def get_xmp_sidecar(self):
        """
        :return: The sidecar xmp file, if it exists. Otherwise None is returned.
        """

        for file in self.files:
            file_extension = file.suffix[1:]
            if file_extension.lower() == 'xmp':
                return file
        return None

    def __str__(self):
        return f'Image: {self.__dict__}'


class ExifImageRegion:
    """
    A rectangular region of an image.
    For example a face tag.
    """

    image: Image

    name: str  # 'John'
    r_type: str  # 'Face'
    area_unit: str  # 'normalized'
    rectangle: List[float]  # [ x-coordinate, y-coordinate, width, height ]

    def __init__(self, image: Image, name, r_type, area_unit, rectangle):
        self.image = image
        self.name = name
        self.r_type = r_type
        self.area_unit = area_unit
        self.rectangle = rectangle

    def __str__(self):
        return f'ExifImageRegion: {self.__dict__}'


def get_exif_image_regions(image: Image) -> List[ExifImageRegion]:
    sidecar: Path = image.get_xmp_sidecar()

    names_str = exec.execute_save(['exiftool', '-RegionName', str(sidecar)])
    r_types_str = exec.execute_save(['exiftool', '-RegionType', str(sidecar)])
    area_units_str = exec.execute_save(['exiftool', '-RegionAreaUnit', str(sidecar)])
    rectangles_str = exec.execute_save(['exiftool', '-RegionRectangle', str(sidecar)])

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

    return [ExifImageRegion(image=image, name=name, r_type=r_type, area_unit=area_unit, rectangle=rectangle) for
            name, r_type, area_unit, rectangle in zip(names, r_types, area_units, rectangles)]
