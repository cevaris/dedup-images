# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python

import hashlib
import os
import pathlib
import pprint
import re
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from typing import List

# exiftool
import exiftool

pp = pprint.PrettyPrinter(indent=4)
CANON_POWERSHOT = 'Canon PowerShot SX50 HS'

class MediaFile(object):
    def __init__(self, id: str, src_path: pathlib.Path, target_path: pathlib.Path):
        self.id = id
        self.src_path = src_path
        self.target_path = target_path

    def __str__(self):
        return "id={} src_path={} target_path={}".format(self.id, self.src_path, self.target_path)

    def __repr__(self):
        return "MediaFile(id={}, src_path={}, target_path={})".format(self.id, self.src_path, self.target_path)

# for Google compressed MOVs and Cannon JPGs
def get_md5(path: pathlib.Path): 
    with open(path, 'rb') as file_to_check:
        data = file_to_check.read()    
        return hashlib.md5(data).hexdigest()

def get_tags(filename: str, md5_store: dict, uuid_store: dict):
    curr_path = pathlib.Path(filename)

    try:
        if 'gif' in curr_path.suffix.lower():
            print('gif', curr_path.name, 'skipping')
            return

        # looks like there are some MOVs that were compressed by Google, and stripped of the metadata
        with exiftool.ExifToolHelper() as et:
            metadata = et.get_metadata(curr_path)
        
            if 'QuickTime:ContentIdentifier' in metadata[0]: # MOV
                uuid = metadata[0]['QuickTime:ContentIdentifier']
                print('video', curr_path, uuid)
                append_media(uuid_store, uuid, curr_path)
                return
            elif 'MakerNotes:MediaGroupUUID' in metadata[0]: # images 
                uuid = metadata[0]['MakerNotes:MediaGroupUUID']
                print('photo', curr_path, uuid)
                append_media(uuid_store, uuid, curr_path)
                return
            elif 'EXIF:Model' in metadata[0] and CANON_POWERSHOT in metadata[0]['EXIF:Model']: # canon
                md5 = get_md5(curr_path)
                print('cannon', curr_path, md5)
                append_media(md5_store, md5, curr_path)
                return
            else:
                md5 = get_md5(curr_path)
                print('unknown', curr_path, md5)
                append_media(md5_store, md5, curr_path)
                return
            
            sys.exit(f'could not categorize {curr_path}')
    except BaseException as error:
        sys.exit("Failed to parse %s - %s" % (filename, error))


def cleanDirectoryPath(dirPath: pathlib.Path):
    """{'december-2019-nz_aus-trip-cris-phone-pics', 'dec-2019-nz_au-trip-album', 'nz-au-adam-photos-all-original', 'auckland-nz-pics'}"""
    return dirPath.name.replace(" ", "-").lower()


def append_media(store: dict, id: str, curr_path: pathlib.Path):
    suffix = curr_path.suffix
    if curr_path.suffix.lower() == '.mov-unknown':
        suffix = '.mov'

    # /Users/adam/Downloads/nz-au/datetime_name_excluded_merge/IMG_3061(1).JPG-nz-au-adam-photos-all-original.JPG
    target_name = "{0}-{1}{2}".format(curr_path.stem,
                                      cleanDirectoryPath(curr_path.parents[0]), suffix)
    target_path = pathlib.Path(os.path.join(TARGET_DIR, target_name))

    key = id.lower()
    media_file = MediaFile(key, curr_path, target_path)
    if key in store:
        store[key].append(media_file)
    else:
        store[key] = [media_file]

def remove_suffix(suffix: str, medias: List[MediaFile]) -> List[MediaFile]:
    return list(filter(lambda x: not suffix in x.src_path.suffix.lower(), medias))

def has_suffix(suffix: str, medias: List[MediaFile]) -> bool:
    return bool(list(filter(lambda x: suffix in x.src_path.suffix.lower(), medias)))

def has_video(medias: List[MediaFile]) -> bool:
    return has_suffix('mov', medias) or has_suffix('mp4', medias)
def has_img(medias: List[MediaFile]) -> bool:
    return has_suffix('jpg', medias) or has_suffix('jpeg', medias) or has_suffix('png', medias) or has_suffix('heic', medias)


TARGET_DIR = f'{pathlib.Path.home()}/Downloads/nz-au/datetime_name_excluded_merge/'
EXCLUSION_DIR = f'{pathlib.Path.home()}/Downloads/nz-au/NZ AU leftovers/'
DIRS = [
    f'{pathlib.Path.home()}/Downloads/nz-au/Auckland NZ Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/Dec 2019 NZ_AU Trip Album',
    f'{pathlib.Path.home()}/Downloads/nz-au/December 2019 NZ_AUS Trip Cris Phone Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/NZ-AU Adam Photos All Original',
]  

include_uuid = {}
exclude_uuid = {}

include_md5 = {}
exclude_md5 = {}

futures = []

executor = ThreadPoolExecutor()


def collect(directory):
    print('collecting', directory)
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        futures.append(executor.submit(get_tags, media_path, include_md5, include_uuid))


for dir in DIRS:
    collect(dir)

print('collecting exclusion dir', EXCLUSION_DIR)
for filename in os.listdir(EXCLUSION_DIR):
    media_path = os.path.join(EXCLUSION_DIR, filename)
    futures.append(executor.submit(get_tags, media_path, exclude_md5, exclude_uuid))

wait(futures)
executor.shutdown()

excpetion_found = False
for f in futures:
    if f.exception():
        print(f.exception())
        excpetion_found = True
if excpetion_found:
    sys.exit(1)

print(f'found {len(exclude_uuid)} excluded uuid media files')
print(f'found {len(exclude_md5)} excluded md5 media files')
print()

print(f'found {len(include_uuid)} uuid media files')
print(f'found {len(include_md5)} md5 media files')
print()

# if media contains key present in exclude_media, skip
exclude_uuid_keys = set(exclude_uuid.keys())
for key in exclude_uuid_keys:
    if key in include_uuid:
        del include_uuid[key]

exclude_md5_keys = set(exclude_md5.keys())
for key in exclude_md5_keys:
    if key in include_md5:
        del include_md5[key]

# for k, v in media.items():
#     # print(k, [f.src_path for f in v])

#     # NOTE: the motion MOV files are timestamped seconds after the photo was taken, so not the same timestmap :(
#     # TODO: determine an algo to find MOVs that are a motion photo
#     # if media contains heic/jpg/jpeg/png & MOV, drop MOV
#     # if media contains heic/jpg/jpeg/png & MP4, drop MP4
#     # if(has_video(v) and has_img(v)):
#     if has_img(v):
#         print('pick image', k, [mf.src_path.name for mf in v])
#         pass

#         # # remove all videos
#         # v = remove_suffix('mov', v)
#         # v = remove_suffix('mp4', v)
#         # media[k] = v

#         # # keep single png/jpg/jpeg/heic
#         # # pick single image
#         # # v = sorted(v, key=lambda m: m.src_path)
#         # print('pick image', k, [mf.src_path.name for mf in v])
#         # pass

#     if(has_video(v)):
#         # pick video
#         print('pick video', k, [mf.src_path.name for mf in v])
#         pass

print(f'found {len(include_uuid)} uuid media files')
print(f'found {len(include_md5)} md5 media files')

pp.pprint(include_uuid)
pp.pprint(include_md5)