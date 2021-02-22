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
    if(len(v) > 1):
        # sort filenames by length for consistency
        # and to get original file
        v = sorted(v, key=lambda x: len(Path(x.media_path).name))
        print(f'{k} -> {[x.media_path for x in v]}')
