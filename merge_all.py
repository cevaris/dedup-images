import os
import pathlib
import shutil
import sys
from pathlib import Path


class MediaFile(object):
    def __init__(self, src_path: Path, target_path: Path):
        self.src_path = src_path
        self.target_path = target_path

    def __str__(self):
        return "src_path={0} target_path={1}".format(self.src_path, self.target_path)


# {'december-2019-nz_aus-trip-cris-phone-pics', 'dec-2019-nz_au-trip-album', 'nz-au-adam-photos-all-original', 'auckland-nz-pics'}
def cleanDirectoryPath(dirPath: Path):
    return dirPath.name.replace(" ", "-").lower()


def collect(directory):
    for filename in os.listdir(directory):
        media_path = os.path.join(directory, filename)
        path = pathlib.Path(media_path)

        suffix = path.suffix
        if(path.suffix.lower() == '.mov-unknown'):
            suffix = '.mov'

        currPath = Path(os.path.join(directory, path.name))
        targetPath = Path(os.path.join(
            TARGET_DIR, "{0}-{1}{2}".format(path.name, cleanDirectoryPath(pathlib.Path(directory)), suffix)))

        media.append(MediaFile(currPath, targetPath))


media = []

TARGET_DIR = sys.argv[1]
collect(sys.argv[2])
collect(sys.argv[3])
collect(sys.argv[4])
collect(sys.argv[5])

for m in media:
    shutil.copy2(m.src_path, m.target_path)

print('done copying', len(media), 'files')
