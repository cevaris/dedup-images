import sys
import os

from PIL import Image
from PIL.ExifTags import TAGS

images = set()


class AnImage(object):
    def __init__(self, model, filename, image_path) -> None:
        super().__init__()
        self.model = model
        self.filename = filename
        self.image_path = image_path

    def __eq__(self, other):
        return self.model == other.model and self.filename == other.filename

    def __hash__(self):
        return hash(('model', self.model, 'filename', self.filename))

    # def __lt__(self, other):
    #     return (self.model, self.filename) < (other.model, other.filename)


# https://www.thepythoncode.com/article/extracting-image-metadata-in-python
def get_model(image_path):
    response = None
    image = Image.open(image_path)

    # desktop screenshots (~10)
    if image_path.endswith(".png"):
        return 'png'

    exifdata = image.getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)

        if tag == 'Model':
            response = exifdata.get(tag_id)
            if isinstance(response, bytes):
                response = response.decode()
            # print(f"{tag}: {response}")

    # edited jpg's (2)
    if response == None:
        return 'unknown'

    return response


def collect(directory):
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)

        model = None
        if image_path.endswith(".mov") or image_path.endswith(".heic") or image_path.endswith(".MOV") or image_path.endswith(".DS_Store"):
            model = 'unknown'
        else:
            model = get_model(image_path)

        images.add(AnImage(model, filename, image_path))


if len(sys.argv) != 3:
    print(sys.argv)
    exit('missing directory arg')

collect(sys.argv[1])
collect(sys.argv[2])

images = list(images)
images = sorted(images, key=lambda x: (x.filename))
print('\n'.join([f'{o.image_path}:{o.model}' for o in images]))
