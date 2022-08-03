# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python

import hashlib
import json
import os
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from enum import Enum
from typing import List

import exiftool

CANON_POWERSHOT = 'Canon PowerShot SX50 HS'

class MediaType(Enum):
     MD5_CANNON_POWERSHOT = 3
     MD5_UNKNOWN = 4
     UUID_CONTENT_IDENTIFIER = 1
     UUID_MEDIA_GROUP_ID = 2

# class MediaMetaFile(object):
#     def __init__(self, id: str, filename: str, media_type: MediaType): 
#         self.id = id
#         self.filename = filename
#         self.media_type = media_type

#     def __str__(self):
#         return "id={} src_path={} target_path={}".format(self.id, self.src_path, self.target_path)

#     def __repr__(self):
#         return "MediaFile(id={}, src_path={}, target_path={})".format(self.id, self.src_path, self.target_path)

#     def __json__(self):
#         return self.__dict__

# for Google compressed MOVs and Cannon JPGs
def get_md5(path: pathlib.Path): 
    with open(path, 'rb') as file_to_check:
        data = file_to_check.read()    
        return hashlib.md5(data).hexdigest()

def get_tags(filename: str, media: List[object]):
    curr_path = pathlib.Path(filename)

    try:
        if 'gif' in curr_path.suffix.lower():
            # print('gif', curr_path.name, 'skipping')
            return

        # looks like there are some MOVs that were compressed by Google, and stripped of the metadata
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(curr_path)
        
            if 'QuickTime:ContentIdentifier' in metadata[0]: # MOV
                uuid = metadata[0]['QuickTime:ContentIdentifier']
                media_meta_files.append({'id': uuid, 'path': filename, 'type': 'UUID_CONTENT_IDENTIFIER'})
                return
            elif 'MakerNotes:MediaGroupUUID' in metadata[0]: # images 
                uuid = metadata[0]['MakerNotes:MediaGroupUUID']
                media_meta_files.append({'id': uuid, 'path': filename, 'type': 'UUID_MEDIA_GROUP_ID'})
                return
            elif 'EXIF:Model' in metadata[0] and CANON_POWERSHOT in metadata[0]['EXIF:Model']: # canon
                md5 = get_md5(curr_path)
                media_meta_files.append({'id': md5, 'path': filename, 'type': 'MD5_CANNON_POWERSHOT'})
                return
            else:
                md5 = get_md5(curr_path)
                media_meta_files.append({'id': md5, 'path': filename, 'type': 'MD5_UNKNOWN'})
                return
            
            sys.exit(f'could not categorize {curr_path}')
    except BaseException as error:
        sys.exit("Failed to parse %s - %s" % (filename, error))

CACHE_FILE = f'{pathlib.Path.home()}/Downloads/nz-au/media_meta_files.json'
EXCLUSION_DIR = f'{pathlib.Path.home()}/Downloads/nz-au/NZ AU leftovers/'
DIRS = [
    f'{pathlib.Path.home()}/Downloads/nz-au/Auckland NZ Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/Dec 2019 NZ_AU Trip Album',
    f'{pathlib.Path.home()}/Downloads/nz-au/December 2019 NZ_AUS Trip Cris Phone Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/NZ-AU Adam Photos All Original',
]  

media_meta_files = []
futures = []
executor = ThreadPoolExecutor()

def collect(directory):
    print('collecting', directory)
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        futures.append(executor.submit(get_tags, media_path, media_meta_files))


for dir in DIRS:
    collect(dir)

print('collecting exclusion dir', EXCLUSION_DIR)
for filename in os.listdir(EXCLUSION_DIR):
    media_path = os.path.join(EXCLUSION_DIR, filename)
    futures.append(executor.submit(get_tags, media_path, media_meta_files))

wait(futures)
executor.shutdown()

excpetion_found = False
for f in futures:
    if f.exception():
        print(f.exception())
        excpetion_found = True
if excpetion_found:
    sys.exit(1)

f = open(CACHE_FILE, "w")
f.write(json.dumps(media_meta_files, indent=4))
f.close()
