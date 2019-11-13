# ytsync
Download YouTube playlists.

Tired of Internet rot destroying your curated playlists?  Download all that
stuff before YouTube strikes down your favorite content with arbitrary TOS
violations, DMCA takedowns, or some bullshit copyright restriction forces the
channel to remove the content.

This tool allows you to scan public playlists and download content to local
storage while you still can.  Run repeatedly in a cron job to incrementally
sync newly added content.

# System Requirements
## Python 3
Required pip module:
```sh
$ pip3 install requests
```

## youtube-dl
Mac OS X:
```sh
$ brew install youtube-dl
```

## ffmpeg
Mac OS X:
```sh
$ brew install ffmpeg
```

# Getting Started
To begin, you will need:
* YouTube Data API key
* Channel id or playlist id

## Create a YouTube Data API Key
https://developers.google.com/youtube/v3/getting-started

## Find the Channel Id
Browse to a channel and the id is in the URL:

```
https://www.youtube.com/channel/<channel_id>
```

## Find the Playlist Id
Browse to a playlist and the id is in the URL:

```
https://www.youtube.com/playlist?list=<playlist_id>
```

Or, use ytsync to browse playlist ids on a channel.

# Usage
```sh
$ python3 ytsync.py -h
```

## List Downloadable Playlists On a Channel
```sh
$ python3 ytsync.py --api-key <key> list-playlists <channel_id>
```

Outputs playlist id and title.

## Sync a Playlist
```sh
$ python3 ytsync.py --api-key <key> sync-playlist <playlist_id>
```

Downloaded content will be downloaded using highest quality available and saved
at file path such as: `download/<playlist>/<video>.mkv`.

If the content has already been downloaded, it will be skipped.  Or, pass
option `-f` to force overwrite.

## Sync All Playlists On a Channel
```sh
$ python3 ytsync.py --api-key <key> sync-channel <channel_id>
```

# Run in Docker
Alternatively, ytsync can be run inside a Docker container.

```sh
$ docker build -t ytsync .
$ docker run --rm ytsync --api-key <key> list-playlists <channel_id>
```

# Customize Video Transcoding
youtube-dl uses ffmpeg to transcode and merge the audio/video streams.  By
default, ytsync will tell youtube-dl to download highest quality streams and
merge to an "mkv" format file.

This behavior can be customized by passing option `--ytdl-args "..."`, such as:

```sh
$ python3 ytsync.py --ytdl-args "-f bestvideo+bestaudio --merge-output-format mkv" ...
```

See [youtube-dl
README](https://github.com/ytdl-org/youtube-dl/blob/master/README.md) for
details.
