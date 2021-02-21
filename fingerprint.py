import sys
import os

from PIL import Image
from PIL.ExifTags import TAGS

print(sys.argv)


if len(sys.argv) != 2:
    exit('missing directory arg')

directory = sys.argv[1]
for filename in os.listdir(directory):
    if filename.endswith(".mov") or filename.endswith(".heic") or filename.endswith(".MOV") or filename.endswith(".DS_Store"):
        continue

    image_path = os.path.join(directory, filename)
    image = Image.open(image_path)

    exifdata = image.getexif()
    for tag_id in exifdata:
        tag = TAGS.get(tag_id, tag_id)

        if tag == 'Model':
            data = exifdata.get(tag_id)
            if isinstance(data, bytes):
                data = data.decode()
            print(f"{tag}: {data}")
