import sys
import shutil
from pathlib import Path


if len(sys.argv) != 2:
    print(sys.argv)
    exit('missing directory arg')

# watch 'ls -l /Users/acardenas/Desktop/union| wc -l'
dest_dir = '/Users/acardenas/Desktop/union/'
filepath = sys.argv[1]
with open(filepath, 'r') as f:
    for line in f:
        image_path, model = line.strip().split(':')
        model = model.replace(' ', '_')

        path = Path(image_path)
        source = path.absolute()
        dest = Path(dest_dir, path.with_name(f'{path.name}-{model}').name)
        shutil.copy(source, dest)
        print(f'{source} => {dest}')
