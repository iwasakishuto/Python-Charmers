#coding: utf-8
import os
import sys
import argparse

from ..utils._path import REPO_DIR
from ..utils.print_utils import Table
sys.path.insert(0, REPO_DIR)
from setup import CONSOLE_SCRIPTS

def show_command_line_programs(argv=sys.argv[1:]):
    """Show all Py-utils's command line programs.

    Args:
        -H/--head (str)  : Show the first ``head`` rows for the table.
        -W/--width (int) : Table width.
        --mark (str)      : The border mark. (default "=")

    Note:
        When you run from the command line, execute as follows::
        
        $ pyutils-show

    """
    parser = argparse.ArgumentParser(prog="pyutils-show", add_help=True)
    parser.add_argument("-H", "--head",  type=int, help="Show the first ``head`` rows for the table.")
    parser.add_argument("-W", "--width", type=int, help="Table width.")
    parser.add_argument("--mark",        type=str, default="=", help='The border mark. (default "=")')
    args = parser.parse_args(argv)

    head = args.head
    table_width = args.width
    mark = args.mark

    commands = []
    paths = []
    for console_script in CONSOLE_SCRIPTS:
        command, path = console_script.split("=")
        commands.append(command)
        paths.append(path)
    table = Table()
    table.set_cols(values=commands, colname="command", color="GREEN")
    table.set_cols(values=paths, colname="path", color="BLUE")
    table.show(head=head, table_width=table_width, mark=mark)
