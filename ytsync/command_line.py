""" Command line entrypoint. """

import argparse
import sys

class YtSyncCli:
    """ CLI class. """
    args: argparse.Namespace

    def _parse_args(self, argv: list[str]) -> None:
        """ Parse command line arguments. """
        # Parse command line arguments.
        parser = argparse.ArgumentParser(description='ytsync')
        parser.add_argument('-d', default='.', help='Download path, default current directory')
        parser.add_argument('--dry-run', action='store_true', help='Dry run, do not download anything')
        parser.add_argument('-v', action='store_true', help='Verbose output')
        parser.add_argument('--ytdlp-args', default='', help='yt-dlp optional arguments')

        self.args = parser.parse_args(argv)

    def __init__(self, argv: list[str]):
        """ Constructor. """
        self._parse_args(argv)

    def run(self):
        """ Run ytsync command. """

        print('Done')

def main() -> int:
    """ Console script entrypoint. """
    argv = sys.argv[1:]
    app = YtSyncCli(argv)
    app.run()
    return 0
