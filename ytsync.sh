#!/bin/bash
# Download from links in input file.
# Archive feature ensures only newly added videos will be downloaded
# because videos are only downloaded once.

DOWNLOAD_PATH=download

YTDL_OPTS="-o ${DOWNLOAD_PATH}/%(playlist)s/%(title)s_%(id)s/%(title)s_%(id)s.%(ext)s --download-archive archive.txt -i --merge-output-format mkv --remux-video aac>m4a/mov>mkv/webm>mkv --write-info-json --write-thumbnail --embed-thumbnail --convert-thumbnails jpg --convert-thumbnails png --embed-metadata --embed-subs --write-subs --write-auto-subs --add-metadata --yes-playlist --cookies cookies.txt"

# Read from STDIN or ytsync_input.
INPUT=ytsync_input
if [ ! -t 0 ]; then
  INPUT=/dev/stdin
fi

while read url; do
  # Skip empty lines and comments.
  [[ $url =~ ^[[:space:]]*(#|$) ]] && continue

  CMD="yt-dlp $YTDL_OPTS $url"
  echo "URL: $url"
  echo $CMD
  $CMD
done <$INPUT

