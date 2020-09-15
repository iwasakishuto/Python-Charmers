#coding: utf-8
import os
import sys
import argparse

from ..utils._path import REPO_DIR
from ..utils.print_utils import Table

with open(os.path.join(REPO_DIR,"console_scripts.txt"), mode="r") as f:
    CONSOLE_SCRIPTS = [line.rstrip("\n") for line in f.readlines() if line[0]!=("#")]
    
def show_command_line_programs(argv=sys.argv[1:]):
    """Show all Python-Charmers's command line programs.

    Args:
        -H/--head (str)  : Show the first ``head`` rows for the table.
        -W/--width (int) : Table width.
        --mark (str)      : The border mark. (default "=")

    Note:
        When you run from the command line, execute as follows::
        
        $ pycharmers-show

    """
    parser = argparse.ArgumentParser(prog="pycharmers-show", add_help=True)
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
