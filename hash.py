import sys
import os
import hashlib
from pathlib import Path


# https://pypi.org/project/ImageHash/
# if we want to remove near duplicates

# https://stackoverflow.com/questions/16874598/how-do-i-calculate-the-md5-checksum-of-a-file-in-python

media = {}


class Media(object):
    def __init__(self, media_path, hash) -> None:
        super().__init__()
        self.media_path = media_path
        self.hash = hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __hash__(self):
        return hash(('hash', self.hash))


def collect(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)

        with open(media_path, 'rb') as fd:
            hash = hashlib.md5(fd.read()).hexdigest()

            if hash in media:
                media[hash].append(Media(media_path, hash))
            else:
                media[hash] = [Media(media_path, hash)]


if len(sys.argv) != 3:
    exit('missing directory arg')

collect(sys.argv[1])
collect(sys.argv[2])

for k, v in media.items():
    # sort filenames by length for consistency
    # and to get original file
    v = sorted(v, key=lambda x: len(Path(x.media_path).name))

    # does not work as hiec/jpg will have different hashes
    # has_hiec = any('hiec' in x.media_path.lower() for x in v)
    # has_jpg = any('jpg' in x.media_path.lower() for x in v)
    # if has_hiec and has_jpg:
    #     # duplicate jpeg/heic, removing jpeg
    #     v = filter(v, lambda x: 'hiec' in x.media_path.lower())
    #     print(f'dropping duplicate jpeg {v}')

    print([x.media_path for x in v][0])
