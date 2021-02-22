import sys
import os
import hashlib

# https://pypi.org/project/ImageHash/
# if we want to remove near duplicates


class Media(object):
    def __init__(self, media_path, hash) -> None:
        super().__init__()
        self.media_path = media_path
        self.hash = hash

    def __eq__(self, other):
        return self.hash == other.hash

    def __hash__(self):
        return hash(('hash', self.hash))


if len(sys.argv) != 2:
    exit('missing directory arg')


media = {}
directory = sys.argv[1]
for filename in os.listdir(directory):
    media_path = os.path.join(directory, filename)

    with open(media_path, 'rb') as fd:
        hash = hashlib.md5(fd.read()).hexdigest()

        if hash in media:
            media[hash].append(Media(media_path, hash))
            # print(
            #     f'{hash} -> {[x.media_path for x in media[hash]]} + {media_path}')
        else:
            media[hash] = [Media(media_path, hash)]

for k, v in media.items():
    if(len(v) > 1):
        print(f'{k} -> {[x.media_path for x in v]}')
