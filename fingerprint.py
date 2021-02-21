import sys
import os

from PIL import Image
from PIL.ExifTags import TAGS


def get_model(image_path):
    image = Image.open(image_path)

    exifdata = image.getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)

        if tag == 'Model':
            data = exifdata.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            print(f"{tag}: {data}")


if len(sys.argv) != 2:
    exit('missing directory arg')

images = []
directory = sys.argv[1]
for filename in os.listdir(directory):
    image_path = os.path.join(directory, filename)

    # if image_path.endswith(".mov") or image_path.endswith(".heic") or image_path.endswith(".MOV") or image_path.endswith(".DS_Store"):
    # continue

    model = get_model(image_path)

    images.append(filename)
    print(model, filename)

images.sort()
print('\n'.join(images))
