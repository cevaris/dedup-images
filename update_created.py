# https://pypi.org/project/pyheif/
# https://github.com/carsales/pyheif/issues/36
# https://www.thepythoncode.com/article/extract-media-metadata-in-python

import io
import os
import pathlib
import sys

# JPEG/PNG
import exifread
# MP4
import ffmpeg
# HIEC
import pyheif
from hachoir.metadata import extractMetadata
# MOV
from hachoir.parser import createParser


def get_tags(filename):
    path = pathlib.Path(filename)

    try:
        if 'gif' in path.suffix.lower():
            print('skipping gif', path)
            return

        if 'mp4' in path.suffix.lower():
            for stream in ffmpeg.probe(filename)["streams"]:
                if stream["tags"]["creation_time"]:
                    # print(path, "Key: creation_date, value %s" %
                    #     (stream["tags"]["creation_time"]))
                    return

        if 'mov' in path.suffix.lower():
            parser = createParser(filename)
            metadata = extractMetadata(parser)
            # print(path, "Key: creation_date, value %s" %
            #       (metadata.get('creation_date')))
            return

        if 'heic' in path.suffix.lower():
            heif_file = pyheif.read(filename)
            for metadata in heif_file.metadata:
                if metadata['type'] == 'Exif':
                    fstream = io.BytesIO(metadata['data'][6:])

                    tags = exifread.process_file(fstream, details=False)
                    for tag in tags.keys():
                        if 'DateTimeOriginal' in tag:
                            # print(path, "Key: %s, value %s" %
                            #       (tag, tags[tag]))
                            return

        with open(filename, 'rb') as f:
            tags = exifread.process_file(f)
            for tag in tags.keys():
                if 'DateTimeOriginal' in tag:
                    # print(path, "Key: %s, value %s" % (tag, tags[tag]))
                    return

    except BaseException as error:
        sys.exit("Failed to parse %s - %s" % (filename, error))

    print('could not parse file', filename)


def collect(directory):
    print('collecting', directory)
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        get_tags(media_path)


collect(sys.argv[1])
