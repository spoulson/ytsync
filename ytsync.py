"""
ytsync.py
Synchronize YouTube playlists on a channel to local storage.
Downloads all videos using youtube-dl.
"""
import argparse
import json
import os
import re
import sys
import requests

class App:
    """ ytsync class """
    args = None

    def list_paginate_items(self, url, headers, params):
        """ Call YouTube Data API and paginate using nextPageToken. """
        items = []

        while True:
            if self.args.v:
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
            'key': self.args.api_key
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
            'key': self.args.api_key
        }

        return self.list_paginate_items(url, headers, params)

    @staticmethod
    def normalize_filename(text):
        """ Normalize string for use as a filename. """
        # Replace forbidden characters.
        text2 = re.sub(r'[\/%]+', '_', text)
        # Replace redundant white space, replace tabs/newlines to spaces.
        text3 = re.sub(r'\s+', ' ', text2)
        return text3

    @staticmethod
    def shell_escape_filename(filename):
        """ Escape filename for use as shell argument. """
        return re.sub(r'(\s|[\\\'"|()<>{}$&#?*`!;])', r'\\\1', filename)

    def download_video(self, video_id, filename):
        """ Download a YouTube video. """
        if not self.args.f and os.path.exists(filename):
            return

        video_url = f'https://youtu.be/{video_id}'
        cmd = f'youtube-dl {self.args.ytdl_args} -o {self.shell_escape_filename(filename)} ' \
                + video_url
        if self.args.v:
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
        playlist_path = os.path.join(self.args.d, self.normalize_filename(playlist_filename))
        video_file = os.path.join(playlist_path, self.normalize_filename(f'{video_filename}.mkv'))
        if self.args.v:
            print(f'Saving to file: {video_file}')

        if not os.path.exists(playlist_path):
            os.makedirs(playlist_path)

        video_id = item['snippet']['resourceId']['videoId']
        try:
            self.download_video(video_id, video_file)
        except RuntimeError as err:
            print(f'Download failed: {str(err)}')

    def cmd_list_playlists(self):
        """ CLI command to list playlists by channel id. """
        playlists = self.list_playlists(channel_id=self.args.channel_id)

        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_title = playlist['snippet']['title']
            print(f'{playlist_id}\t{playlist_title}')

    def cmd_sync_playlist(self):
        """ CLI command to sync playlist. """
        playlist_id = self.args.playlist_id
        playlists = self.list_playlists(playlist_ids=[playlist_id])
        if not playlists:
            print(f'Playlist not found')
            return

        playlist = playlists[0]
        playlist_id = playlist['id']
        items = self.list_playlist_items(playlist_id)

        for item in items:
            video_title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']

            if item['status']['privacyStatus'] == 'private':
                print(f'Skipping private video id "{video_id}"')
                continue

            print(f'Found video "{video_title}"')
            self.download_playlist_item(playlist, item)

    def cmd_sync_channel(self):
        """ CLI command to sync all playlists in a channel. """
        playlists = self.list_playlists(channel_id=self.args.channel_id)

        for playlist in playlists:
            playlist_id = playlist['id']
            items = self.list_playlist_items(playlist_id)

            for item in items:
                video_title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']

                if item['status']['privacyStatus'] == 'private':
                    print(f'Skipping private video id "{video_id}"')
                    continue

                print(f'Found video "{video_title}"')
                self.download_playlist_item(playlist, item)

    def __init__(self):
        """ Constructor. """
        # Parse command line arguments.
        parser = argparse.ArgumentParser(description='ytsync')
        parser.add_argument('--api-key', required=True, help='YouTube API key (required)')
        parser.add_argument('-d', default='download', help='Download path, default "download"')
        parser.add_argument('-f', action='store_true', help='Force overwrite existing downloads')
        parser.add_argument('-v', action='store_true', help='Verbose output')
        parser.add_argument('--ytdl-args',
                            default='-f bestvideo+bestaudio --merge-output-format mkv',
                            help='youtube-dl optional arguments'
                            )
        subparsers = parser.add_subparsers(dest='command', required=True)

        parser_list_playlists = \
            subparsers.add_parser('list-playlists',
                                  help='List playlists in a channel'
                                  )
        parser_list_playlists.add_argument(dest='channel_id')

        parser_sync_channel = \
            subparsers.add_parser('sync-channel',
                                  help='Sync all playlists in a channel'
                                  )
        parser_sync_channel.add_argument(dest='channel_id')

        parser_sync_playlist = subparsers.add_parser('sync-playlist', help='Sync a playlist')
        parser_sync_playlist.add_argument(dest='playlist_id')

        self.args = parser.parse_args(sys.argv[1:])

    def main(self):
        """ Entrypoint. """
        # Dispatch command.
        command = self.args.command
        if command == 'list-playlists':
            self.cmd_list_playlists()

        elif command == 'sync-channel':
            self.cmd_sync_channel()

        elif command == 'sync-playlist':
            self.cmd_sync_playlist()

        print('Done')

# Call entrypoint.
APP = App()
APP.main()
