
import os
import sys
from multiprocessing import Pool
import pathlib
import re


p = re.compile(r'(IMG_(\d){4})')


def collect(directory):
    media = {}
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        name = pathlib.Path(media_path).name

        match = p.search(name)
        if match:
            key = match.group(1)
            if key in media:
                media[key].append(media_path)
            else:
                media[key] = [media_path]
    return media


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
    # does not work as heic/jpg will have different hashes
    has_hiec = any('.heic' in x.lower() for x in v)
    has_jpg = any('.jpg' in x.lower() for x in v)

    if has_hiec and has_jpg:
        # duplicate jpeg/heic, removing jpg
        # print('before', v)
        v = filter(lambda x: 'EFFECTS' in x.lower() or '.jpg' not in x.lower(), v)
        # print('after', list(v))
        # print(f'dropping duplicate jpg {k}\n')

    for f in v:
        print(f)
    # print()
