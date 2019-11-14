"""
ytsync.py
Synchronize YouTube playlists on a channel to local storage.
Downloads all videos using youtube-dl.
"""
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

class Ytsync:
    """ ytsync application class """
    verbose = False
    force = False
    api_key = None
    target_path = '.'
    ytdl_args = '-f bestvideo+bestaudio --merge-output-format mkv'

    def list_paginate_items(self, url, headers, params):
        """ Call YouTube Data API and paginate using nextPageToken. """
        items = []

        while True:
            if self.verbose:
                print(f'API url: {url}, params: {params}')

            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                raise Exception(f'API error {response.status_code} at url: {url}')

            content = json.loads(response.content)
            items = items + content['items']

            if not 'nextPageToken' in content:
                break

            if 'pageToken' in params and params['pageToken'] == content['nextPageToken']:
                raise Exception('Endless loop detected.  nextPageToken isn\'t updating.')

            params['pageToken'] = content['nextPageToken']

        return items

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
            raise Exception('Must specify channel_id or playlist_ids')

        return self.list_paginate_items(url, headers, params)

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

        return self.list_paginate_items(url, headers, params)

    def download_video(self, video_id, filename):
        """ Download a YouTube video. """
        if not self.force and os.path.exists(filename):
            return

        video_url = f'https://youtu.be/{video_id}'
        cmd = f'youtube-dl {self.ytdl_args} -o {shell_escape_filename(filename)} ' \
                + video_url
        if self.verbose:
            print(cmd)

        os.system(cmd)

        # Verify file was created.
        if not os.path.exists(filename):
            raise RuntimeError(f'File was not created: {filename}')

    def download_playlist_item(self, playlist, item):
        """ Download all videos in a YouTube playlist. """
        # Determine download file path.
        playlist_filename = playlist['snippet']['title']
        video_filename = item['snippet']['title']
        playlist_path = os.path.join(self.target_path, normalize_filename(playlist_filename))
        video_file = os.path.join(playlist_path, normalize_filename(f'{video_filename}.mkv'))
        if self.verbose:
            print(f'Saving to file: {video_file}')

        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)

        video_id = item['snippet']['resourceId']['videoId']
        try:
            self.download_video(video_id, video_file)
        except RuntimeError as err:
            print(f'Download failed: {str(err)}')
