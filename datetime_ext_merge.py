import os
import pathlib
import shutil
import sys
from datetime import datetime
from pathlib import Path
import cv2

class MediaFile(object):
    def __init__(self, created_at: datetime, src_path: Path, target_path: Path):
        self.created_at = created_at
        self.src_path = src_path
        self.target_path = target_path

    def __str__(self):
        return "created_at={} src_path={} target_path={}".format(self.created_at, self.src_path, self.target_path)

    def __repr__(self):
        return "MediaFile(created_at={}, src_path={}, target_path={})".format(self.created_at, self.src_path, self.target_path)


# {'december-2019-nz_aus-trip-cris-phone-pics', 'dec-2019-nz_au-trip-album', 'nz-au-adam-photos-all-original', 'auckland-nz-pics'}
def cleanDirectoryPath(dirPath: Path):
    return dirPath.name.replace(" ", "-").lower()

def with_opencv(filename):
    video = cv2.VideoCapture(filename)

    duration = video.get(cv2.CAP_PROP_POS_MSEC)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)

    return duration, frame_count


def collect(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        path = pathlib.Path(media_path)

        suffix = path.suffix
        if path.suffix.lower() == '.mov-unknown':
            suffix = '.mov'

        if '.mov' in suffix:
            print(with_opencv(media_path))

        created_at = datetime.utcfromtimestamp(os.path.getmtime(media_path))
        src_path = Path(os.path.join(directory, path.name))
        target_path = Path(os.path.join(
            TARGET_DIR, "{0}-{1}{2}".format(path.name, cleanDirectoryPath(pathlib.Path(directory)), suffix)))

        key = f'{created_at}:{path.name.lower()}'

        if key in media:
            media[key].append(
                MediaFile(created_at, src_path, target_path))
        else:
            media[key] = [MediaFile(created_at, src_path, target_path)]


def exclude(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        path = pathlib.Path(media_path)

        suffix = path.suffix
        if path.suffix.lower() == '.mov-unknown':
            suffix = '.mov'

        created_at = datetime.utcfromtimestamp(os.path.getmtime(media_path))
        src_path = Path(os.path.join(directory, path.name))
        target_path = Path(os.path.join(
            TARGET_DIR, "{0}-{1}{2}".format(path.name, cleanDirectoryPath(pathlib.Path(directory)), suffix)))

        key = f'{created_at}:{path.name.lower()}'

        if key in media:
            media[key].append(
                MediaFile(created_at, src_path, target_path))
        else:
            media[key] = [MediaFile(created_at, src_path, target_path)]

# datetime -> MediaFile[]
media = {}
excluded_media = {}

TARGET_DIR = sys.argv[1]
collect(sys.argv[2])
collect(sys.argv[3])
collect(sys.argv[4])
collect(sys.argv[5])

# for m in media:
#    shutil.copy2(m.src_path, m.target_path)
# print('done copying', len(media), 'files')

for k, v in media.items():
    v = sorted(v, key=lambda m: m.src_path)
    # print(k, v[0].target_path)
    # m = v[0]
    # shutil.copy2(m.src_path, m.target_path)

    # print(len(v), k)

    # if len(v) > 2:
    #     for m in v:
    #         print(m)

    # print(k)
    # for m in v:
    #     print(m)
    # print()
