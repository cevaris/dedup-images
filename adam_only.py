import os
import sys
from multiprocessing import Pool
import pathlib
import exifread

"""
Extracting Adam only media will not work as MOV files do not include model names.
"""


# p = re.compile(r'(IMG_(\d){4})')
sets = set()

def get_model(media_path): 
    with open(media_path, 'rb') as fd:
            tags = exifread.process_file(fd)
            for tag in tags.keys():
                if 'Image Model' in tag:
                    return str(tags[tag])


def collect(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        model = get_model(media_path)

        sets.add(model)
        

        if not model:
            print(media_path)
    print(sets)

        
if len(sys.argv) != 5:
    exit('missing directory arg')

with Pool(5) as p:
    maps = p.map(collect, [sys.argv[1], sys.argv[2], sys.argv[3]])
    # print(len(maps), len(maps[0]), len(maps[1]), len(maps[2]))
    print(sets)

    # # merge results
    # media = maps[0]
    # for k, v in maps[1].items():
    #     if k in media:
    #         media[k] = media[k] + v
    #     else:
    #         media[k] = [v]

    # for k, v in maps[2].items():
    #     if k in media:
    #         media[k] = media[k] + v
    #     else:
    #         media[k] = [v]

    # for k, v in media.items():
    #     # sort filenames by length for consistency
    #     # and to get original file
    #     try:
    #         v = sorted(v, key=lambda x: len(pathlib.Path(x).name))
    #         for f in v:
    #             print(f)
    #         print()
    #     except Exception as ex: 
    #         print(ex, v)
    #         raise ex

