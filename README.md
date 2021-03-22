# dedup-images

Some python to deduplicate some home pics

Dedup process

- hash uniq images + videos
- duplicate heic and jpg
  -- go through ~/Desktop/hash-all.txt list, match on IMG_XXXX.ext
  -- if ext includes both heic and jpg, drop jpg

# Dedup files based off md5 hash

python3 ./hash.py ~/Downloads/NZ-AU\ Adam\ Photos\ All\ Original ~/Downloads/December\ 2019\ NZ_AUS\ Trip\ \(Cris\ Phone\ Pics\) ~/Downloads/Dec\ 2019\ NZ_AU\ Trip\ Album  ~/Downloads/Auckland\ NZ\ Pics > ~/Desktop/hash-all.txt

# (skipping) Dedupe duplicate heic and jpg images based off IMG_XXXX id

python3 ./heic_dedup_hash.py ~/Desktop/hash-all.txt > ~/Desktop/final-copy.txt

# copy deduped images to new directory

python3 ./copy_files.py ~/Desktop/final-copy.txt

# copy abnormal file names

grep EFFECTS ~/Desktop/hash-all.txt | xargs -I{} cp -f {} ~/Downloads/union
