# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python

import io
import os
import pathlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor, wait
from datetime import datetime
from typing import List

# JPEG/PNG
import exifread
# MP4
import ffmpeg
# heic
import pyheif
from hachoir.metadata import extractMetadata
# MOV
from hachoir.parser import createParser


class MediaFile(object):
    def __init__(self, created_at: datetime, src_path: pathlib.Path, target_path: pathlib.Path):
        self.created_at = created_at
        self.src_path = src_path
        self.target_path = target_path

    def __str__(self):
        return "created_at={} src_path={} target_path={}".format(self.created_at, self.src_path, self.target_path)

    def __repr__(self):
        return "MediaFile(created_at={}, src_path={}, target_path={})".format(self.created_at, self.src_path, self.target_path)


def get_tags(filename: str, store: dict):
    curr_path = pathlib.Path(filename)

    try:
        if 'gif' in curr_path.suffix.lower():
            print('skipping gif', curr_path)
            return

        # NOTE looks like Leftovers is the only one with a .mp4 suffix
        # TODO: confirm if MP4s are seemingly 11 hours behind the photos
        if 'mp4' in curr_path.suffix.lower():
            for stream in ffmpeg.probe(filename)["streams"]:

                # NOTE: We should filter live motion videos elsehow. There are some videos that are short lengthed.
                # # skip live motion MP4 files
                # if float(stream['duration']) < 4:
                #     return

                if stream["tags"]["creation_time"]:
                    # 2019-12-09T03:58:04.000000Z
                    created_at_str = stream["tags"]["creation_time"]
                    created_at = datetime.strptime(
                        created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ'
                    )
                    append_media(store, created_at, curr_path)
                    # print ('found mp4', curr_path, created_at)
                    return

        # TODO: confirm why MOV is seemingly 11 hours behind the photos
        #       Looks like Media Group UUID && Content Identifier could be match mov/photos
        #       https://github.com/photoprism/photoprism/issues/1885
        if 'mov' in curr_path.suffix.lower():
            parser = createParser(filename)
            metadata = extractMetadata(parser)

            # NOTE: We should filter live motion videos elsehow. There are some videos that are short lengthed.
            # # skip live motion MOV files
            # if metadata.get("duration").total_seconds() < 3:
            #     print(path, 'skipping live motion', metadata.get("duration").total_seconds())
            #     return

            # 2019-12-11 03:03:41
            created_at = metadata.get('creation_date')
            # print(curr_path, created_at, metadata.get(
            #     'duration').total_seconds())
            append_media(media, created_at, curr_path)
            return

        if 'heic' in curr_path.suffix.lower():
            heif_file = pyheif.read(filename)
            for metadata in heif_file.metadata:
                if metadata['type'] == 'Exif':
                    fstream = io.BytesIO(metadata['data'][6:])

                    tags = exifread.process_file(fstream, details=False)
                    for tag in tags.keys():
                        # print(curr_path, "Key: %s, value %s" %
                        #       (tag, tags[tag]))
                        if 'DateTimeOriginal' in tag:
                            created_at_str = str(tags[tag])
                            created_at = datetime.strptime(
                                created_at_str, '%Y:%m:%d %H:%M:%S'
                            )
                            # print(path, created_at_str, created_at)
                            append_media(store, created_at, curr_path)
                            return

        if curr_path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            with open(filename, 'rb') as f:
                tags = exifread.process_file(f)
                for tag in tags.keys():
                    # print(path, "Key: %s, value %s" % (tag, tags[tag]))
                    if 'DateTimeOriginal' in tag:
                        created_at_str = str(tags[tag])
                        created_at = datetime.strptime(
                            created_at_str, '%Y:%m:%d %H:%M:%S'
                        )
                        append_media(store, created_at, curr_path)
                        return

    except BaseException as error:
        sys.exit("Failed to parse %s - %s" % (filename, error))

    print('could not parse file', filename)


def cleanDirectoryPath(dirPath: pathlib.Path):
    """{'december-2019-nz_aus-trip-cris-phone-pics', 'dec-2019-nz_au-trip-album', 'nz-au-adam-photos-all-original', 'auckland-nz-pics'}"""
    return dirPath.name.replace(" ", "-").lower()


def append_media(store: dict, created_at: datetime, curr_path: pathlib.Path):
    suffix = curr_path.suffix
    if curr_path.suffix.lower() == '.mov-unknown':
        suffix = '.mov'

    target_name = "{0}-{1}{2}".format(curr_path.name,
                                      cleanDirectoryPath(curr_path.parents[0]), suffix)
    target_path = pathlib.Path(os.path.join(TARGET_DIR, target_name))

    media_file = MediaFile(created_at, curr_path, target_path)

    # NOPE: since we have timestamps for every file, we should be able to dedup per created_at
    # key = created_at
    # NOTE: truncate seconds since MOV motion files comes in with a few seconds of difference of the photos
    created_at_key = created_at.strftime("%Y-%m-%d %H:%M") # '2022-07-19 14:13'
    # NOTE: we do need to inclue filename here given there are photos taken at the same second, same camera
    # TODO: strip out (\([0-9])\) from the filename for key hashing
    dup_imgage_regex = r'(\([0-9])\)'
    file_name_key = re.sub(dup_imgage_regex, '', curr_path.stem).lower()
    key = f'{created_at_key}:{file_name_key}'
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
# datetime:image => MediaFile[]
media = {}
exclude_media = {}
futures = []

executor = ThreadPoolExecutor()


def collect(directory):
    print('collecting', directory)
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        futures.append(executor.submit(get_tags, media_path, media))


for dir in DIRS:
    collect(dir)

print('collecting exclusion dir', EXCLUSION_DIR)
for filename in os.listdir(EXCLUSION_DIR):
    media_path = os.path.join(EXCLUSION_DIR, filename)
    futures.append(executor.submit(get_tags, media_path, exclude_media))

wait(futures)
executor.shutdown()

excpetion_found = False
for f in futures:
    if f.exception():
        print(f.exception())
        excpetion_found = True
if excpetion_found:
    sys.exit(1)

pass

print(f'found {len(media)} media files')
print(dict(list(media.items())[0:50]).keys())
print(f'found {len(exclude_media)} exluced media files')
print(dict(list(exclude_media.items())[0:50]).keys())

# if media contains key present in exclude_media, skip
exclude_media_keys = set(exclude_media.keys())
for key in exclude_media_keys:
    if key in media:
        del media[key]


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

# print(f'found {len(media)} media files')
# print(dict(list(media.items())[0:50]).keys())
