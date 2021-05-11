#coding: utf-8
import os
import sys
import argparse

from ..utils._path import REPO_DIR
from ..utils.generic_utils import str_strip
from ..utils.print_utils import Table

with open(os.path.join(REPO_DIR, "console_scripts.txt"), mode="r") as f:
    CONSOLE_SCRIPTS = [line.strip("\n") for line in f.readlines() if line[0]!=("#")]

def show_command_line_programs(argv=sys.argv[1:]):
    """Show all Python-Charmers's command line programs.

    Args:
        -H/--head (str)      : Show the first ``head`` rows for the table.
        -W/--width (int)     : Table width.
        --description (bool) : Whether to show description or path. (default= ``False`` )
        --tablefmt (str)     : Table format.

    Note:
        When you run from the command line, execute as follows::
        
        $ pycharmers-show

    Examples:
        >>> $ pycharmers-show
        +---------------------+------------------------------------------------------+
        |       command       |                         path                         |
        +=====================+======================================================+
        |            book2img | pycharmers.cli.book2img:book2img                     |
        +---------------------+------------------------------------------------------+
        |         cv-cascades | pycharmers.cli.cvCascades:cvCascades                 |
        +---------------------+------------------------------------------------------+
        |    cv-paper-scanner | pycharmers.cli.cvPaperScanner:cvPaperScanner         |
        +---------------------+------------------------------------------------------+
        |    cv-pencil-sketch | pycharmers.cli.cvPencilSketch:cvPencilSketch         |
        +---------------------+------------------------------------------------------+
        |           cv-window | pycharmers.cli.cvWindow:cvWindow                     |
        +---------------------+------------------------------------------------------+
        |          lyricVideo | pycharmers.cli.lyricVideo:lyricVideo                 |
        +---------------------+------------------------------------------------------+
        |   form-auto-fill-in | pycharmers.cli.form_auto_fill_in:form_auto_fill_in   |
        +---------------------+------------------------------------------------------+
        |         openBrowser | pycharmers.cli.openBrowser:openBrowser               |
        +---------------------+------------------------------------------------------+
        |             pdfmine | pycharmers.cli.pdfmine:pdfmine                       |
        +---------------------+------------------------------------------------------+
        |  regexp-replacement | pycharmers.cli.regexp_replacement:regexp_replacement |
        +---------------------+------------------------------------------------------+
        |     render-template | pycharmers.cli.render_template:render_template       |
        +---------------------+------------------------------------------------------+
        | requirements-create | pycharmers.cli.requirements:requirements_create      |
        +---------------------+------------------------------------------------------+
        |     pycharmers-show | pycharmers.cli.show:show_command_line_programs       |
        +---------------------+------------------------------------------------------+
        |            tweetile | pycharmers.cli.tweetile:tweetile                     |
        +---------------------+------------------------------------------------------+
        |           video2gif | pycharmers.cli.video2gif:video2gif                   |
        +---------------------+------------------------------------------------------+
    """
    parser = argparse.ArgumentParser(prog="pycharmers-show", add_help=True)
    parser.add_argument("-H", "--head",  type=int, help="Show the first ``head`` rows for the table.")
    parser.add_argument("-W", "--width", type=int, help="Table width.")
    parser.add_argument("--description", action="store_true", help="Whether to show description or path. (default= ``False`` )")
    parser.add_argument("--tablefmt", choices=Table.SUPPORTED_FORMATS, default="github", help="The format of table.")
    args = parser.parse_args(argv)

    head = args.head
    table_width = args.width
    # mark = args.mark

    paths       = []
    commands    = []
    descriptons = []
    for console_script in CONSOLE_SCRIPTS:
        command, path = [str_strip(e) for e in console_script.split("=")]
        commands.append(command)
        paths.append(path)
        f,i = path.split(":")
        exec(f"from {f} import {i}")
        descriptons.append(eval(f"{i}.__doc__.split('\\n')[0]"))

    table = Table(tablefmt=args.tablefmt)
    table.set_cols(values=commands, colname="command", color="GREEN")
    if args.description:
        table.set_cols(values=descriptons, colname="description", color="BLUE", align="left")
    else:
        table.set_cols(values=paths, colname="path", color="BLUE", align="left")
    table.show(head=head, table_width=table_width)
