#!/usr/bin/env python3


"""
NOTE: 
script to be ran post-handbrake processing to preserve original unprocessed metadata
based on https://superuser.com/a/523696

NOTE: exiftool must be installed on the system, install via brew:
```
brew install exiftool
```
"""

import os
import sys

if len(sys.argv) != 3:
    print("Usage: copy_meta.py <RAW_DIR> <PROCESSED_DIR>")
    sys.exit(1)

RAW_DIR = sys.argv[1]
PROCESSED_DIR = sys.argv[2]

OUTPUT_DIR = f"{PROCESSED_DIR}-meta"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def copy_meta(raw_file_path, processed_file_path):
    # use ffmpeg -map_metadata to copy metadata from raw_file to processed_file
    # patched_file_path  = os.path.join(f"{PROCESSED_DIR}-meta", os.path.basename(processed_file_path))
    # os.system(f"ffmpeg -i {raw_file_path} -i {processed_file_path} -map 1 -movflags use_metadata_tags -map_metadata 0 -c copy {patched_file_path}")
    os.system(f"exiftool -tagsFromFile {raw_file_path} -GPSLatitude -GPSLongitude -GPSCoordinates -GPSPosition -time:all -geotag:all {processed_file_path}")


raw_files = os.listdir(RAW_DIR)
processed_files = os.listdir(PROCESSED_DIR)


for raw_file_name in raw_files:
    raw_file_path = os.path.join(RAW_DIR, raw_file_name)
    processed_file_path = os.path.join(PROCESSED_DIR, raw_file_name)
    print("raw_file: " + raw_file_path)
    print("processed_file: " + processed_file_path)

    if "mp4" in raw_file_path.lower():
        copy_meta(raw_file_path, processed_file_path)
