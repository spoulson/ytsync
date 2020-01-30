""" YouTube API client. """
import datetime
import json
import os
import re

import requests

def normalize_filename(text):
    """ Normalize string for use as a filename. """
    # Replace forbidden characters.
    text2 = re.sub(r'[\/%]+', '_', text)
    # Replace redundant white space, replace tabs/newlines to spaces.
    text3 = re.sub(r'\s+', ' ', text2)
    return text3

def shell_escape_filename(filename):
    """ Escape filename for use as shell argument. """
    return re.sub(r'(\s|[\\\'"|()<>{}$&#?*`!;])', r'\\\1', filename)

def write_metadata_file(meta_filename, item, video_filename):
    """ Write YouTube video metadata to file. """
    if os.path.exists(meta_filename):
        # Do not overwrite.
        return

    metadata = {
        'video_file': video_filename,
        'create_date': datetime.datetime.now().isoformat(),
        'youtube_playlist_item': item
    }
    with open(meta_filename, 'w') as mfile:
        mfile.write(json.dumps(metadata))

    return

class ListPaginateIterator:
    """ Iterate over paginated list calls in YouTube Data API. """
    def __init__(self, url, headers, params, verbose=False):
        self.url = url
        self.headers = headers
        self.params = params
        self.verbose = verbose
        self.buffer = []
        self.eof = False

    def __iter__(self):
        return self

    def __fetch_page(self):
        items = []

        if self.verbose:
            print(f'API url: {self.url}, params: {self.params}')

        response = requests.get(self.url, params=self.params, headers=self.headers)
        if response.status_code != 200:
            raise RuntimeError(f'API error {response.status_code} at url: {self.url}')

        content = json.loads(response.content)
        items = items + content['items']

        if not 'nextPageToken' in content:
            self.eof = True
        else:
            if 'pageToken' in self.params and self.params['pageToken'] == content['nextPageToken']:
                raise RuntimeError('Endless loop detected.  nextPageToken isn\'t updating.')

            self.params['pageToken'] = content['nextPageToken']

        return items

    def __next__(self):
        if not self.buffer:
            if self.eof: raise StopIteration

            self.buffer = self.__fetch_page()

            if not self.buffer: raise StopIteration

        return self.buffer.pop(0)

class YtApi:
    """ YouTube API client """
    verbose = False
    force = False
    api_key = None
    target_path = '.'
    ytdl_args = '-f bestvideo+bestaudio --merge-output-format mkv'
    dry_run = False

    def list_playlists(self, channel_id=None, playlist_ids=None):
        """ Call YouTube Data API to list playlists by either channel id or playlist ids. """
        url = 'https://www.googleapis.com/youtube/v3/playlists'
        headers = {'Content-Type': 'application/json'}
        params = {
            'part': 'contentDetails,snippet',
            'maxResults': 50,
            'key': self.api_key
        }
        if channel_id is not None:
            params['channelId'] = channel_id
        elif playlist_ids is not None:
            params['id'] = ','.join(playlist_ids)
        else:
            raise ValueError('Must specify channel_id or playlist_ids')

        # return self.list_paginate_items(url, headers, params)
        return ListPaginateIterator(url, headers, params, verbose=self.verbose)

    def list_playlist_items(self, playlist_id):
        """ Call YouTube Data API to list playlist items. """
        url = 'https://www.googleapis.com/youtube/v3/playlistItems'
        headers = {'Content-Type': 'application/json'}
        params = {
            'playlistId': playlist_id,
            'part': 'contentDetails,snippet,status',
            'maxResults': 50,
            'key': self.api_key
        }

        return ListPaginateIterator(url, headers, params, verbose=self.verbose)

    def download_video(self, video_id, filename):
        """ Download a YouTube video. """
        if not self.force and os.path.exists(filename):
            return

        video_url = f'https://youtu.be/{video_id}'
        cmd = f'youtube-dl {self.ytdl_args} -o {shell_escape_filename(filename)} ' \
                + video_url
        if self.verbose:
            print(cmd)

        if not self.dry_run:
            os.system(cmd)

            # Verify file was created.
            if not os.path.exists(filename):
                raise RuntimeError(f'File was not created: {filename}')

    def download_playlist_item(self, playlist, item, options):
        """ Download all videos in a YouTube playlist. """
        options2 = {
            'no_metadata': False,
            'no_video': False,
            **options
        }

        # Determine download filenames.
        playlist_filename = playlist['snippet']['title']
        video_filename = item['snippet']['title']
        playlist_path = os.path.join(self.target_path, normalize_filename(playlist_filename))
        norm_video_basename = normalize_filename(video_filename)
        norm_video_filename = f'{norm_video_basename}.mkv'
        video_file = os.path.join(playlist_path, norm_video_filename)
        if self.verbose:
            print(f'Saving to file: {video_file}')

        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)

        if not options2['no_metadata']:
            # Write metadata to file.
            metadata_file = os.path.join(playlist_path, f'{norm_video_basename}.meta.json')
            write_metadata_file(metadata_file, item, norm_video_filename)

        if not options2['no_video']:
            # Capture video file.
            video_id = item['snippet']['resourceId']['videoId']
            try:
                self.download_video(video_id, video_file)
            except RuntimeError as err:
                print(f'Download failed: {str(err)}')
