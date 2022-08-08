# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python


# NOTE: to be used with file_exiftool.py; which collects the metadata from the files
#       and dumps it to a json file. This is then used to create the media_metadata_dict
#       dictionary below for quick processing.

import hashlib
import json
import os
import pathlib
import pprint
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from typing import List

pp = pprint.PrettyPrinter(indent=4)

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
            # print('gif', curr_path.name, 'skipping')
            return

        # looks like there are some MOVs that were compressed by Google, and stripped of the metadata
        metadata = media_metadata_dict[filename]
    
        if metadata['type'] == 'UUID_CONTENT_IDENTIFIER': # MOV
            uuid = metadata['id']
            # print('video', curr_path, uuid)
            append_media(uuid_store, uuid, curr_path)
            return
        elif metadata['type'] == 'UUID_MEDIA_GROUP_ID': # images 
            uuid = metadata['id']
            # print('photo', curr_path, uuid)
            append_media(uuid_store, uuid, curr_path)
            return
        elif metadata['type'] == 'MD5_CANNON_POWERSHOT': # canon
            md5 = metadata['id']
            # print('cannon', curr_path, md5)
            append_media(md5_store, md5, curr_path)
            return
        else:
            md5 = metadata['id']
            # print('unknown', curr_path, md5)
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

def pick_img(medias: List[MediaFile]) -> MediaFile:
    return list(filter(lambda x: x.target_path.suffix.lower() in ['.jpeg', '.jpg', '.png', '.heic'], medias))[0]
def pick_video(medias: List[MediaFile]) -> MediaFile:
    return list(filter(lambda x: x.target_path.suffix.lower() in ['.mov', '.mp4'], medias))[0]


def post_process(store: dict):
    for k, v in store.items():
        # if media contains heic/jpg/jpeg/png & MOV, drop MOV
        # if media contains heic/jpg/jpeg/png & MP4, drop MP4
        if(has_video(v) and has_img(v)):
            img = pick_img(v)
            video = pick_video(v)
            print(f'pick id={k} img={img.target_path} video={video.target_path}')
            # shutil.copy2(img.src_path, img.target_path)
            # shutil.copy2(video.src_path, video.target_path)
            continue

        if has_img(v):
            img = pick_img(v)
            print(f'pick id={k} img={img.target_path}')
            # shutil.copy2(img.src_path, img.target_path)
            continue

        if(has_video(v)):
            video = pick_video(v)
            print(f'pick id={k} video={video.target_path}')
            # shutil.copy2(video.src_path, video.target_path)
            continue


CACHE_FILE = f'{pathlib.Path.home()}/Downloads/nz-au/media_meta_files.json'
TARGET_DIR = f'{pathlib.Path.home()}/Downloads/nz-au/final_datetime_name_excluded_merge/'
EXCLUSION_DIR = f'{pathlib.Path.home()}/Downloads/nz-au/NZ AU leftovers/'
DIRS = [
    f'{pathlib.Path.home()}/Downloads/nz-au/Auckland NZ Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/Dec 2019 NZ_AU Trip Album',
    f'{pathlib.Path.home()}/Downloads/nz-au/December 2019 NZ_AUS Trip Cris Phone Pics',
    f'{pathlib.Path.home()}/Downloads/nz-au/NZ-AU Adam Photos All Original',
]  

# filepath -> metadata
media_metadata_dict = {}
with open(CACHE_FILE) as f:
    lines = f.readlines()
    media_metadata_list = json.loads(''.join(lines)) 
    for media_metadata in media_metadata_list:
        media_metadata_dict[media_metadata['path']] = media_metadata

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
        get_tags(media_path, include_md5, include_uuid)


for dir in DIRS:
    collect(dir)

print('collecting exclusion dir', EXCLUSION_DIR)
for filename in os.listdir(EXCLUSION_DIR):
    media_path = os.path.join(EXCLUSION_DIR, filename)
    get_tags(media_path, exclude_md5, exclude_uuid)

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

print(f'found {len(include_uuid)} uuid media files')
post_process(include_uuid)
# pp.pprint(include_uuid)

print(f'found {len(include_md5)} md5 media files')
post_process(include_md5)
# pp.pprint(include_md5)
