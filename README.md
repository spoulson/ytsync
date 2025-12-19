# ytsync
Automated download of YouTube videos and playlists.

Tired of Internet rot destroying your curated playlists?  Download all that
stuff before YouTube strikes down your favorite content with arbitrary TOS
violations, DMCA takedowns, or some bullshit copyright restriction forces the
channel to remove the content.

This tool allows you to scan public playlists and download content to local
storage while you still can.  Run repeatedly in a cron job to incrementally
sync newly added content.

# Pre-requisites
## yt-dlp
MacOS:
```sh
$ brew install pipx
$ pipx install yt-dlp
```

Ubuntu:
```sh
$ sudo apt install pipx
$ pipx install yt-dlp
```

## ffmpeg
MacOS:
```sh
$ brew install ffmpeg
```

Ubuntu:
```sh
$ sudo apt install ffmpeg
```

# Getting Started
## Build input list
Create file `ytsync_input`.  Each line contains a URL to a YouTube video,
channel, or playlist.  Additionally, the URL could go to any other video site
that `yt-dlp` supports.

Lines can be empty or commented out with `#` character.  I recommend placing a
comment line before each link as a description.

# Customize Video Metadata and Transcoding
Inspect `ytsync.sh` for customizations to `YTDL_OPTS`.  This values is passed
as parameters to `yt-dlp`.

The default settings in `YTDL_OPTS` is optimized for easy file organization
across multiple channels, playlists, and individual videos, all useful
metadata, and optimum audio/video quality.

Read more about yt-dlp: https://github.com/yt-dlp/yt-dlp

# Other Scripts
## `get.sh`
Ad hoc download video URL to a playlist directory.

Usage: `./get.sh <playlist_name> <URL>`

## `convert_thumbnails.sh`
Special script to convert videos downloaded with `webp` format thumbnail files.
Because Plex Media Server does not support `webp`, this script converts those
to `jpg`.

`YTDL_OPTS` is set to download thumbnails as `jpg` or `png`, but if they are
downloaded as `webp` due to a misconfiguration then this script can correct
those.

