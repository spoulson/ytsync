# ytsync.py
# Synchronize YouTube playlists on a channel to local storage.
# Downloads all videos using youtube-dl.

import argparse
import json
import os
import re
import requests
import sys

# Parse command line arguments.
parser = argparse.ArgumentParser(description='ytsync')
parser.add_argument('--api-key', required=True, help='YouTube API key (required)')
parser.add_argument('-d', default='download', help='Download path, default "download"')
parser.add_argument('-f', action='store_true', help='Force overwrite existing downloads')
parser.add_argument('-v', action='store_true', help='Verbose output')
parser.add_argument('--ytdl-args', default='-f bestvideo+bestaudio --merge-output-format mkv', help='youtube-dl optional arguments')
subparsers = parser.add_subparsers(dest='command', required=True)

parser_list_playlists = subparsers.add_parser('list-playlists', help='List playlists in a channel')
parser_list_playlists.add_argument(dest='channel_id')

parser_sync_channel = subparsers.add_parser('sync-channel', help='Sync all playlists in a channel')
parser_sync_channel.add_argument(dest='channel_id')

parser_sync_playlist = subparsers.add_parser('sync-playlist', help='Sync a playlist')
parser_sync_playlist.add_argument(dest='playlist_id')

args = parser.parse_args(sys.argv[1:])

api_key = args.api_key
target_path = args.d
force = args.f
verbose = args.v
ytdl_args = args.ytdl_args

def list_paginate_items(url, headers, params):
	items = []

	while True:
		if verbose:
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

def list_playlists(api_key, channel_id = None, playlist_ids = None):
	url = 'https://www.googleapis.com/youtube/v3/playlists'
	headers = { 'Content-Type': 'application/json' }
	params = {
			'part': 'contentDetails,snippet',
			'maxResults': 50,
			'key': api_key
			}
	if channel_id != None:
		params['channelId'] = channel_id
	elif playlist_ids != None:
		params['id'] = ','.join(playlist_ids)
	else:
		raise Exception('Must specify channel_id or playlist_ids')

	return list_paginate_items(url, headers, params)

def list_playlist_items(api_key, playlist_id):
	url = 'https://www.googleapis.com/youtube/v3/playlistItems'
	headers = { 'Content-Type': 'application/json' }
	params = {
			'playlistId': playlist_id,
			'part': 'contentDetails,snippet,status',
			'maxResults': 50,
			'key': api_key
			}

	return list_paginate_items(url, headers, params)

# Normalize string for use as a filename.
def normalize_filename(text):
	# Replace forbidden characters.
	text2 = re.sub(r'[\/%]+', '_', text)
	# Replace redundant white space, replace tabs/newlines to spaces.
	text3 = re.sub(r'\s+', ' ', text2)
	return text3

def get_playlist_filename(playlist):
	playlist_id = playlist['id']
	playlist_title = playlist['snippet']['title']
	return playlist_title

def get_playlist_item_filename(item):
	video_id = item['snippet']['resourceId']['videoId']
	video_title = item['snippet']['title']
	return video_title

def shell_escape_filename(filename):
	return re.sub(r'(\s|[\\\'"|()<>{}$&#?*`!;])', r'\\\1', filename)

def download_video(video_id, filename):
	if not force and os.path.exists(filename):
		return

	video_url = f'https://youtu.be/{video_id}'
	cmd = f'youtube-dl {ytdl_args} -o {shell_escape_filename(filename)} {video_url}'
	if verbose:
		print(cmd)

	os.system(cmd)

	# Verify file was created.
	if not os.path.exists(filename):
		raise Exception(f'File was not created: {filename}')

def download_playlist_item(api_key, playlist, item):
	# Determine download file path.
	playlist_filename = get_playlist_filename(playlist)
	video_filename = get_playlist_item_filename(item)
	playlist_path = os.path.join(target_path, normalize_filename(playlist_filename))
	video_file = os.path.join(playlist_path, normalize_filename(f'{video_filename}.mkv'))
	if verbose:
		print(f'video_file: {video_file}')

	if not os.path.exists(playlist_path):
		os.makedirs(playlist_path)

	video_id = item['snippet']['resourceId']['videoId']
	try:
		download_video(video_id, video_file)
	except Exception as e:
		print(f'Download failed: {str(e)}')

def cmd_list_playlists(channel_id):
	playlists = list_playlists(api_key, channel_id=channel_id)

	for playlist in playlists:
		playlist_id = playlist['id']
		playlist_title = playlist['snippet']['title']
		print(f'{playlist_id}\t{playlist_title}')

	return

def cmd_sync_playlist(playlist_id):
	playlists = list_playlists(api_key, playlist_ids=[playlist_id])
	if not playlists:
		print(f'Playlist not found')
		return

	playlist = playlists[0]
	playlist_id = playlist['id']
	items = list_playlist_items(api_key, playlist_id)

	for item in items:
		video_title = item['snippet']['title']
		video_id = item['snippet']['resourceId']['videoId']

		if item['status']['privacyStatus'] == 'private':
			print(f'Skipping private video id "{video_id}"')
			continue

		print(f'Found video "{video_title}"')
		download_playlist_item(api_key, playlist, item)

	return

def cmd_sync_channel(channel_id):
	playlists = list_playlists(api_key, channel_id=channel_id)

	for playlist in playlists:
		playlist_id = playlist['id']
		items = list_playlist_items(api_key, playlist_id)

		for item in items:
			video_title = item['snippet']['title']
			video_id = item['snippet']['resourceId']['videoId']

			if item['status']['privacyStatus'] == 'private':
				print(f'Skipping private video id "{video_id}"')
				continue

			print(f'Found video "{video_title}"')
			download_playlist_item(api_key, playlist, item)

	return

# Dispatch commands.
if args.command == 'list-playlists':
	cmd_list_playlists(args.channel_id)

elif args.command == 'sync-channel':
	cmd_sync_channel(args.channel_id)

elif args.command == 'sync-playlist':
	cmd_sync_playlist(args.playlist_id)

sys.exit(0)
