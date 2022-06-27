import os
import sys
import shutil
from pathlib import Path


if len(sys.argv) != 2:
    print(sys.argv)
    exit('missing directory arg')

# watch 'ls -l /Users/acardenas/Downloads/union| wc -l'
dest_dir = '/Users/acardenas/Downloads/union-hash/'
os.mkdir(dest_dir)

filepath = sys.argv[1]
with open(filepath, 'r') as f:
    for line in f:
        path = Path(line.strip())
        source = path.absolute()
        dest = Path(dest_dir, path.name)
        shutil.copy(source, dest)
        print(f'{source} => {dest}')
