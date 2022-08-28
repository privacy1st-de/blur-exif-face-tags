from pathlib import Path


class ImageFiles:
    """
    An image may be just a single file (e.g. "IMG_001.RAF") or
    multiple files ("IMG_002.JPG" (image-data) and
    "IMG_002.JPG.xmp" (additional metadata)).
    """

    files: list[Path]

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
            raise Exception(f'Not a file: {image_file}')

    def get_image_file(self):
        return self.files[0]

    def get_xmp_file(self):
        """
        :return: The sidecar xmp file, if it exists. Otherwise, `None` is returned.
        """
        for file in self.files:
            file_extension = file.suffix[1:]
            if file_extension.lower() == 'xmp':
                return file
        return None

    def get_metadata_file(self):
        """
        If a sidecar xmp file exists, it is preferred over the image file itself.

        :return: A file containing the image metadata.
        """
        metadata = self.get_xmp_file()
        if metadata is None:
            metadata = self.get_image_file()
        return metadata

    def __str__(self):
        return f'Image: {self.__dict__}'
