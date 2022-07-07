# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python

import io
import os
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

# JPEG/PNG
import exifread
# MP4
import ffmpeg
# HIEC
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


def get_tags(filename):
    path = pathlib.Path(filename)

    try:
        if 'gif' in path.suffix.lower():
            print('skipping gif', path)
            return

        if 'mp4' in path.suffix.lower():
            return
            for stream in ffmpeg.probe(filename)["streams"]:
                if stream["tags"]["creation_time"]:
                    # 2019-12-09T03:58:04.000000Z
                    created_at_str = stream["tags"]["creation_time"]
                    created_at = datetime.strptime(
                        created_at_str, '%Y-%m-%dT%H:%M:%S.%fZ'
                    )
                    append_media(created_at, path)
                    return

        if 'mov' in path.suffix.lower():
            return
            parser = createParser(filename)
            metadata = extractMetadata(parser)
            # 2019-12-11 03:03:41
            created_at = metadata.get('creation_date')
            print(path, created_at)
            return

        if 'heic' in path.suffix.lower():
            return
            heif_file = pyheif.read(filename)
            for metadata in heif_file.metadata:
                if metadata['type'] == 'Exif':
                    fstream = io.BytesIO(metadata['data'][6:])

                    tags = exifread.process_file(fstream, details=False)
                    for tag in tags.keys():
                        if 'DateTimeOriginal' in tag:
                            created_at_str = str(tags[tag])
                            created_at = datetime.strptime(
                                created_at_str, '%Y:%m:%d %H:%M:%S'
                            )
                            print(path, created_at_str, created_at)
                            return

        if path.suffix.lower() in ['.jpg', '.jpeg', '.png']:
            with open(filename, 'rb') as f:
                tags = exifread.process_file(f)
                for tag in tags.keys():
                    if 'DateTimeOriginal' in tag:
                        created_at_str = str(tags[tag])
                        created_at = datetime.strptime(
                            created_at_str, '%Y:%m:%d %H:%M:%S'
                        )
                        print(path, created_at_str, created_at)
                        # print(path, "Key: %s, value %s" % (tag, tags[tag]))
                        return

    except BaseException as error:
        sys.exit("Failed to parse %s - %s" % (filename, error))

    print('could not parse file', filename)


def cleanDirectoryPath(dirPath: pathlib.Path):
    """{'december-2019-nz_aus-trip-cris-phone-pics', 'dec-2019-nz_au-trip-album', 'nz-au-adam-photos-all-original', 'auckland-nz-pics'}"""
    return dirPath.name.replace(" ", "-").lower()


def append_media(created_at: datetime, path: pathlib.Path):
    media_file = MediaFile(created_at, path, path)
    key = f'{created_at}:{path.name.lower()}'
    if key in media:
        media[key].append(media_file)
    else:
        media[key] = [media_file]


# datetime:image => MediaFile[]
media = {}
executor = ThreadPoolExecutor()


def collect(directory):
    print('collecting', directory)
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        executor.submit(get_tags, media_path)
    executor.shutdown()


collect(sys.argv[1])