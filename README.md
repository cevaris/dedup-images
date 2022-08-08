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


# Media
- [NZ AU leftovers-001.zip](https://drive.google.com/file/d/1rh-ekr_Xiw2gq7jjXN2qkrFo_HXAFvWg/view?usp=sharing)
  - Originally uploaded content, that still has live-motion photos, and misc videos. This was used to prevent uploading locally dedupled data, that has already been uploaded.
- [final-dedup-missing-media-with-live-motion.zip](https://drive.google.com/file/d/1OX_C71uYJPN8nYYqG6PQBygd3zQsT95v/view)
  - Final dataset. This dataset was not uploaded as is, rather live-motion videos were removed from live pics first, then it was  uploaded. So only live motion pics (without paired videos) and actual non-motion video recordings were uploaded. This zip contains all deduplicated locally and previously uploaded "NZ AU leftovers" media.
- [Auckland NZ Pics.zip](https://drive.google.com/file/d/15nz1PnP3NqlfaUVhpCHuRwsIbNwKZHhQ/view?usp=sharing)
  - Random media
- [Dec 2019 NZ_AU Trip Album.zip](https://drive.google.com/file/d/1IjxjyxVfXWmhfLGDcO_CTqhq8Ur5_wc3/view?usp=sharing)
  - Random media
- [December 2019 NZ_AUS Trip (Cris Phone Pics).zip](https://drive.google.com/file/d/1URfwUV-3yxxRcUX4dMIbT3U8XAZBw4EJ/view?usp=sharing) 
  - Random media
- [NZ-AU Adam Photos All Original-001.zip](https://drive.google.com/file/d/1KHWbzGvpNNNgOawb6s-jAq5trhCEFmV_/view?usp=sharing)
  - Random media


# Aug 8, 2022 update
- I was able to correclty map each live motion with live photo, and dedup the non live photos via md5 finger prints. 
- Google Photos does not have an open API for uploading live photos :( So best i can do is save stills for now (without video), in the chance Google Photos adds live photo upload in the future. 
- Overall, this adds 734 missing still photos + actual non-live motion videos.
- ./file_exiftool.py collects the required exif tags into a json file
- ./metadata_uuid_match.py looks at that exif tags json file and quickly dedupes on the exif tags or fingerprints. 
- this seemingly is the right solution as the resulting media is indeed missing from Google Photos.
- upon uploading, the media should sync to the correct date/time, and I can re-create the album to share. 
- [final-dedup-missing-media-with-live-motion.zip](https://drive.google.com/file/d/1OX_C71uYJPN8nYYqG6PQBygd3zQsT95v/view) has the media generated from this codebase, of which has been deduped from both local and originally uploaded "leftovers" content, but live motion videos was preserved in this zip file. Live motion videos were stripped from today (8/8/22) upload since Google does not allow uploading merged live motions, only the iOS Google photos app allows that. Note, live motion videos were not uploaded. To get live motion photos and non-motion video media, just use ./file_exiftool.py and ./metadata_uuid_match.py tool again on the final_datetime_name_excluded_merge_stills set. 