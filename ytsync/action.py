""" Ytsync action. """

import os
import shlex

from yt_dlp import _real_main as yt_dlp_main  # type: ignore


class YtsyncAction:
    """ Call yt-dlp to do a download. """
    verbose: bool
    dry_run: bool
    download_path: str
    ytdlp_args: list[str]

    def __init__(self, verbose: bool, dry_run: bool, download_path: str,
                 ytdlp_args: list[str]):
        """ Constructor. """
        self.verbose = verbose
        self.dry_run = dry_run
        self.download_path = download_path
        self.ytdlp_args = ytdlp_args

    def run(self, content_urls: list[str]) -> None:
        """ Run ytsync action. """
        argv: list[str] = []

        if self.verbose:
            argv.append('-v')
        if self.download_path != '':
            argv += ['-P', self.download_path]
        argv += [
                '-o', '%(playlist)s/%(title)s.%(ext)s',
                '--download-archive', os.path.join(self.download_path, 'archive.txt'),
                '--cookies', os.path.join(self.download_path, 'cookies.txt'),
                '-i',
                '--write-info-json',
                '--write-thumbnail',
                '--add-metadata',
                '--yes-playlist'
        ]
        argv += self.ytdlp_args
        argv += content_urls

        if self.dry_run:
            argstr = stringify_argv(argv)
            print(f'Dry run action: yt-dlp {argstr}')
            return

        yt_dlp_main(argv)

def stringify_argv(argv: list[str]) -> str:
    """ Convert argv to human readable string. """
    return ' '.join(map(shlex.quote, argv))
