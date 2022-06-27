import os
import pathlib
import sys
from pathlib import Path


class MediaFile(object):
    def __init__(self, src_path, target_path):
        self.src_path = src_path
        self.target_path = target_path

    def __str__(self):
        return "src_path={0} target_path={1}".format(self.src_path, self.target_path)


def cleanDirectoryPath(dirPath: Path):
    return dirPath.name.replace(" ", "-").lower()


def collect(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        name = pathlib.Path(media_path).name

        currPath = os.path.join(directory, name)
        targetPath = os.path.join(
            TARGET_DIR, "{0}-{1}".format(cleanDirectoryPath(pathlib.Path(directory)), name))

        media.append(MediaFile(currPath, targetPath))


media = []

TARGET_DIR = sys.argv[1]
collect(sys.argv[2])

for m in media:
    print(m)
