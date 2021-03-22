import os
import sys
from multiprocessing import Pool


def collect(directory):
    media = set()
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)

        if 'heic' in media_path.lower():
            media.add(media_path)
    return media


if len(sys.argv) != 3:
    exit('missing directory arg')

sets = None
with Pool(5) as p:
    sets = p.map(collect, [sys.argv[1], sys.argv[2]])

    # generate set union
    sets[0].update(sets[1])

    for v in sets[0]:
        print(v)
