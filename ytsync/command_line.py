""" Command line entrypoint. """

import argparse
import re
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
        parser.add_argument('-i', dest='input_filename', default=None,
                            help='File input containing many content URLs.')
        parser.add_argument('content_urls', metavar='URL', nargs='*',
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

        content_urls = self.args.content_urls

        if self.args.input_filename is not None:
            # File input.
            content_urls += _read_input_file(self.args.input_filename)

        action.run(content_urls)
        print('Done')


def _read_input_file(filename: str) -> list[str]:
    """
    Read input file.
    Exclude blank lines or comment lines.
    """
    lines = []

    if filename == '-':
        file = sys.stdin
    else:
        file = open(filename, 'r', encoding='utf-8')  # pylint: disable=consider-using-with

    skip_re = re.compile(r'^([ #-]|$)')

    for line in file:
        if skip_re.match(line):
            continue

        lines.append(line)

    if filename != '-':
        file.close()

    return lines

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
