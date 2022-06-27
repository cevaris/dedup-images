
import pathlib
import re
import sys

import exifread

p = re.compile(r'(IMG_(\d){4})')

def get_model(media_path):
    with open(media_path, 'rb') as fd:
        tags = exifread.process_file(fd)
        for tag in tags.keys():
            if 'Image Model' in tag:
                return str(tags[tag])


if len(sys.argv) != 2:
    exit('incorrect params')

media = {}
with open(sys.argv[1]) as f:
    for line in f:
        media_path = line.strip()
        path = pathlib.Path(media_path)

        match = p.search(path.name)
        if match:
            key = match.group(1)
            if key in media:
                media[key].append(media_path)
            else:
                media[key] = [media_path]

for k, v in media.items():
    for f in v: 
        print(k, f, get_model(f))
    print()

    # does not work as heic/jpg will have different hashes
    # has_hiec = any('.heic' in x.lower() for x in v)
    # has_jpg = any('.jpg' in x.lower() for x in v)

    # if has_hiec and has_jpg:
    #     # duplicate jpeg/heic, removing jpg
    #     # print('before', v)
    #     v = filter(lambda x: 'EFFECTS' in x.lower()
    #                or '.jpg' not in x.lower(), v)
    #     # print('after', list(v))
    #     # print(f'dropping duplicate jpg {k}\n')

    # for f in v:
    #     print(f)
    # print()
