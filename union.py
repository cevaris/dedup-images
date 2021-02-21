import sys
import os

from PIL import Image
from PIL.ExifTags import TAGS

images = set()


def get_model(image_path):
    response = None
    image = Image.open(image_path)

    exifdata = image.getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)

        if tag == 'Model':
            response = exifdata.get(tag_id)
            if isinstance(response, bytes):
                response = response.decode()
            # print(f"{tag}: {response}")

    return response


def collect(directory):
    for filename in os.listdir(directory):
        image_path = os.path.join(directory, filename)

        model = None
        if image_path.endswith(".mov") or image_path.endswith(".heic") or image_path.endswith(".MOV") or image_path.endswith(".DS_Store"):
            model = 'unknown'
        else:
            model = get_model(image_path)

        key = f"{model}:{filename}"
        images.add(key)
        # print(key)


if len(sys.argv) != 3:
    print(sys.argv)
    exit('missing directory arg')

collect(sys.argv[1])
collect(sys.argv[2])

images = list(images)
images.sort()
print('\n'.join(images))
