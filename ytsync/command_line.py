""" Command line entrypoint. """

import argparse
import shlex
import sys

import loguru
from .action import YtsyncAction


class YtsyncCli:
    """ CLI class. """
    args: argparse.Namespace

    def _parse_args(self, argv: list[str]) -> None:
        """ Parse command line arguments. """
        # Parse command line arguments.
        parser = argparse.ArgumentParser(description='ytsync')
        parser.add_argument('-d', dest='download_path', default='.',
                            help='Download path, default current directory')
        parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                            help='Dry run, do not download anything')
        parser.add_argument('-v', dest='verbose', action='store_true',
                            help='Verbose output')
        parser.add_argument('--ytdlp-args', dest='ytdlp_args', default='',
                            help='yt-dlp optional arguments')
        parser.add_argument('content_urls', metavar='URL', nargs='+',
                            help='Content URLs.')

        self.args = parser.parse_args(argv)

    def __init__(self, argv: list[str]):
        """ Constructor. """
        self._parse_args(argv)

    def run(self) -> None:
        """ Run ytsync command. """
        ytdlp_argv = shlex.split(self.args.ytdlp_args)
        action = YtsyncAction(verbose=self.args.verbose,
                              dry_run=self.args.dry_run,
                              download_path=self.args.download_path,
                              ytdlp_args=ytdlp_argv)
        action.run(self.args.content_urls)
        print('Done')


def init_logging() -> None:
    """ Initialize loguru. """
    loguru.logger.configure(
        handlers=[
            dict(
                sink=sys.stdout,
                format='<white><green>{time:YYYY-MM-DD HH:mm:ss}</green> '
                       + '<level>{level.icon:<5}</level> <dim>|</dim> '
                       + '{message}</white>\n'
            )
        ],
        levels=[
            dict(name="DEBUG", icon="DEBUG"),
            dict(name="INFO", icon="INFO"),
            dict(name="WARNING", icon="WARN"),
            dict(name="ERROR", icon="ERROR")
        ]
    )


def main() -> int:
    """ Console script entrypoint. """
    init_logging()

    argv = sys.argv[1:]
    app = YtsyncCli(argv)
    app.run()
    return 0
