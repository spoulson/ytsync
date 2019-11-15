""" Command line entrypoint. """

import argparse
import os
import sys
from . import Ytsync

class YtsyncCli:
    """ CLI class. """
    args = None
    ytsync = None

    def cmd_list_playlists(self):
        """ CLI command to list playlists by channel id. """
        playlists = self.ytsync.list_playlists(channel_id=self.args.channel_id)

        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_title = playlist['snippet']['title']
            print(f'{playlist_id}\t{playlist_title}')

    def cmd_sync_playlist(self):
        """ CLI command to sync playlist. """
        playlist_id = self.args.playlist_id
        playlists = self.ytsync.list_playlists(playlist_ids=[playlist_id])
        if not playlists:
            print(f'Playlist not found')
            return

        playlist = playlists[0]
        playlist_id = playlist['id']
        items = self.ytsync.list_playlist_items(playlist_id)

        for item in items:
            video_title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']

            if item['status']['privacyStatus'] == 'private':
                print(f'Skipping private video id "{video_id}"')
                continue

            print(f'Found video "{video_title}"')
            self.ytsync.download_playlist_item(playlist, item)

    def cmd_sync_channel(self):
        """ CLI command to sync all playlists in a channel. """
        playlists = self.ytsync.list_playlists(channel_id=self.args.channel_id)

        for playlist in playlists:
            playlist_id = playlist['id']
            items = self.ytsync.list_playlist_items(playlist_id)

            for item in items:
                video_title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']

                if item['status']['privacyStatus'] == 'private':
                    print(f'Skipping private video id "{video_id}"')
                    continue

                print(f'Found video "{video_title}"')
                self.ytsync.download_playlist_item(playlist, item)

    def parse_args(self):
        """ Parse command line arguments. """
        # Parse command line arguments.
        parser = argparse.ArgumentParser(description='ytsync')
        parser.add_argument('--api-key', help='YouTube API key')
        parser.add_argument('-d', default='download', help='Download path, default "download"')
        parser.add_argument('-f', action='store_true', help='Force overwrite existing downloads')
        parser.add_argument('-v', action='store_true', help='Verbose output')
        parser.add_argument('--ytdl-args', default='', help='youtube-dl optional arguments')
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

    def __init__(self):
        """ Constructor. """
        self.parse_args()

        # Build Ytsync object.
        self.ytsync = Ytsync()
        self.ytsync.verbose = self.args.v
        self.ytsync.force = self.args.f

        if self.args.api_key is not None:
            self.ytsync.api_key = self.args.api_key
        elif 'API_KEY' in os.environ:
            self.ytsync.api_key = os.environ['API_KEY']
        else:
            raise ValueError('API key is required')

        self.ytsync.target_path = self.args.d
        if self.args.ytdl_args != '':
            self.ytsync.ytdl_args = self.args.ytdl_args

    def run(self):
        """ Run ytsync. """
        # Dispatch command.
        command = self.args.command
        if command == 'list-playlists':
            self.cmd_list_playlists()

        elif command == 'sync-channel':
            self.cmd_sync_channel()

        elif command == 'sync-playlist':
            self.cmd_sync_playlist()

        print('Done')

def main():
    """ Console script entrypoint. """
    app = YtsyncCli()
    app.run()
