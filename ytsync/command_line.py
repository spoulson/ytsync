""" Command line entrypoint. """

import argparse
import datetime
import os
import sys

from chronyk import Chronyk
import iso8601
import pytz
from .ytapi import YtApi

class PlaylistItemFilter:
    """ Playlist item filter. """
    added_since = None
    published_since = None
    name = None
    published_on_channel_id = None
    is_public = True

    def test(self, item):
        """ Test playlist item for filter match. """
        if self.name is not None:
            if not self.name.lower() in item['snippet']['title'].lower():
                return False

        if self.added_since is not None:
            added_dt = iso8601.parse_date(item['snippet']['publishedAt'])
            if added_dt < self.added_since:
                return False

        if self.published_since is not None:
            published_dt = iso8601.parse_date(item['contentDetails']['videoPublishedAt'])
            if published_dt < self.published_since:
                return False

        return True

def build_item_filter(args):
    """ Parse arguments for playlist item filter criteria. """
    item_filter = PlaylistItemFilter()
    if args.added_since is not None:
        item_filter.added_since = datetime.datetime.fromtimestamp(
            Chronyk(args.added_since).timestamp(),
            pytz.utc
        )
    if args.published_since is not None:
        item_filter.published_since = datetime.datetime.fromtimestamp(
            Chronyk(args.published_since).timestamp(),
            pytz.utc
        )
    if args.name is not None:
        item_filter.name = args.name

    return item_filter

class YtSyncCli:
    """ CLI class. """
    args = None
    ytapi = None

    def cmd_list_playlists(self):
        """ CLI command to list playlists by channel id. """
        playlists = self.ytapi.list_playlists(channel_id=self.args.channel_id)

        for playlist in playlists:
            playlist_id = playlist['id']
            playlist_title = playlist['snippet']['title']
            print(f'{playlist_id}\t{playlist_title}')

    def cmd_sync_playlist(self):
        """ CLI command to sync playlist. """
        playlist_id = self.args.playlist_id
        playlists = self.ytapi.list_playlists(playlist_ids=[playlist_id])
        if not playlists:
            print(f'Playlist not found')
            return

        playlist = list(playlists)[0]
        playlist_id = playlist['id']

        # Parse filter criteria.
        item_filter = build_item_filter(self.args)

        # Iterate items.
        items = self.ytapi.list_playlist_items(playlist_id)
        for item in items:
            if item_filter is not None and not item_filter.test(item):
                continue

            video_title = item['snippet']['title']
            video_id = item['snippet']['resourceId']['videoId']

            if item['status']['privacyStatus'] == 'private':
                print(f'Skipping private video id "{video_id}"')
                continue

            print(f'Found video "{video_title}"')
            self.ytapi.download_playlist_item(playlist, item)

    def cmd_sync_channel(self):
        """ CLI command to sync all playlists in a channel. """
        playlists = self.ytapi.list_playlists(channel_id=self.args.channel_id)

        # Parse filter criteria.
        item_filter = build_item_filter(self.args)

        # Iterate playlists.
        for playlist in playlists:
            playlist_id = playlist['id']

            # Iterate items.
            items = self.ytapi.list_playlist_items(playlist_id)
            for item in items:
                if item_filter is not None and not item_filter.test(item):
                    continue

                video_title = item['snippet']['title']
                video_id = item['snippet']['resourceId']['videoId']

                if item['status']['privacyStatus'] == 'private':
                    print(f'Skipping private video id "{video_id}"')
                    continue

                print(f'Found video "{video_title}"')
                self.ytapi.download_playlist_item(playlist, item)

    def parse_args(self):
        """ Parse command line arguments. """
        # Parse command line arguments.
        parser = argparse.ArgumentParser(description='ytsync')
        parser.add_argument('--api-key', help='YouTube API key')
        parser.add_argument('-d', default='download', help='Download path, default "download"')
        parser.add_argument('--dry-run', action='store_true', help='Dry run, do not download anything')
        parser.add_argument('-f', action='store_true', help='Force overwrite existing downloads')
        parser.add_argument('-v', action='store_true', help='Verbose output')
        parser.add_argument('--ytdl-args', default='', help='youtube-dl optional arguments')
        subparsers = parser.add_subparsers(dest='command', required=True)

        parser_list_playlists = \
            subparsers.add_parser('list-playlists',
                                  help='List playlists in a channel')
        parser_list_playlists.add_argument(dest='channel_id', help='Channel id to list')

        parser_sync_channel = \
            subparsers.add_parser('sync-channel',
                                  help='Sync all playlists in a channel')
        parser_sync_channel.add_argument(dest='channel_id', help='Channel id to sync')
        parser_sync_channel.add_argument('--added-since', help='Filter videos added to playlist since timestamp')
        parser_sync_channel.add_argument('--published-since', help='Filter videos published since timestamp')
        parser_sync_channel.add_argument('--name', help='Filter video names matching substring case-insensitive')

        parser_sync_playlist = subparsers.add_parser('sync-playlist', help='Sync a playlist')
        parser_sync_playlist.add_argument(dest='playlist_id', help='Playlist id to sync')
        parser_sync_playlist.add_argument('--added-since', help='Filter videos added to playlist since timestamp')
        parser_sync_playlist.add_argument('--published-since', help='Filter videos published since timestamp')
        parser_sync_playlist.add_argument('--name', help='Filter video names matching substring case-insensitive')

        self.args = parser.parse_args(sys.argv[1:])

    def __init__(self):
        """ Constructor. """
        self.parse_args()

        # Build Ytsync object.
        self.ytapi = YtApi()
        self.ytapi.verbose = self.args.v
        self.ytapi.force = self.args.f
        self.ytapi.dry_run = self.args.dry_run

        if self.args.api_key is not None:
            self.ytapi.api_key = self.args.api_key
        elif 'API_KEY' in os.environ:
            self.ytapi.api_key = os.environ['API_KEY']
        else:
            raise ValueError('API key is required')

        self.ytapi.target_path = self.args.d
        if self.args.ytdl_args != '':
            self.ytapi.ytdl_args = self.args.ytdl_args

    def run(self):
        """ Run ytsync command. """
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
    app = YtSyncCli()
    app.run()
