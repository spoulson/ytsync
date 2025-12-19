#!/bin/sh

category=$1
url=$2
title=${3:-%(title)s_%(id)s}

DOWNLOAD_PATH=download
YTDL_OPTS="--download-archive archive.txt -i --merge-output-format mkv --remux-video aac>m4a/mov>mkv/webm>mkv --write-info-json --write-thumbnail --embed-thumbnail --convert-thumbnails jpg --convert-thumbnails png --embed-metadata --embed-subs --write-subs --write-auto-subs --add-metadata --yes-playlist --cookies cookies.txt"

if [ -z "$category" ] || [ -z "$url" ]; then
  echo "Usage: $0 <category> <url> [title]" >&2
  exit 1
fi

set -x
yt-dlp $YTDL_OPTS -o "${DOWNLOAD_PATH}/${category}/${title}/${title}.%(ext)s" $url
