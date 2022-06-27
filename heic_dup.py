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

        if '-unknown' in media_path:
            continue

        match = p.search(name)
        if match:
            key = match.group(1)
            if key in media:
                media[key].append(media_path)
            else:
                media[key] = [media_path]
    return media


if len(sys.argv) != 5:
    exit('missing directory arg')

sets = None
with Pool(5) as p:
    maps = p.map(collect, [sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]])
    print(len(maps), len(maps[0]), len(maps[1]), len(maps[2]), len(maps[3]))

    # merge results
    media = maps[0]
    for k, v in maps[1].items():
        if k in media:
            media[k] = media[k] + v
        else:
            media[k] = [v]

    for k, v in maps[2].items():
        if k in media:
            media[k] = media[k] + v
        else:
            media[k] = [v]

    for k, v in maps[3].items():
        if k in media:
            media[k] = media[k] + v
        else:
            media[k] = [v]

    for k, v in media.items():
        # sort filenames by length for consistency
        # and to get original file
        try:
            v = sorted(v, key=lambda x: len(pathlib.Path(x).name))
            for f in v:
                print(f)
            print()
        except Exception as ex: 
            print(ex, v)
            raise ex

