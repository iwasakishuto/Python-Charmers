#coding: utf-8
import os
import re
import sys
import argparse

from ..__meta__ import __documentation__ as BASE_URL
from ..utils._path import REPO_DIR, CLI_DIR
from ..utils.generic_utils import str_strip
from ..utils.print_utils import Table
from ..utils.soup_utils import get_soup

from typing import List, Tuple

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
        +---------------------+----------------------------------------------------------------------------------+
        |       command       |                                   description                                    |
        +=====================+==================================================================================+
        |            book2img | Convert Book into Sequential Images.                                             |
        +---------------------+----------------------------------------------------------------------------------+
        |         cv-cascades | Control the OpenCV cascade Examples.                                             |
        +---------------------+----------------------------------------------------------------------------------+
        |    cv-paper-scanner | Paper Scanner using OpenCV.                                                      |
        +---------------------+----------------------------------------------------------------------------------+
        |    cv-pencil-sketch | Convert the image like a pencil drawing.                                         |
        +---------------------+----------------------------------------------------------------------------------+
        |           cv-window | Use :meth:`cvWindow <pycharmers.opencv.windows.cvWindow>` to control frames.     |
        +---------------------+----------------------------------------------------------------------------------+
        |   form-auto-fill-in | Auto fill in your form using your saved information (or answer on the spot).     |
        +---------------------+----------------------------------------------------------------------------------+
        |     jupyter-arrange | Arrange Jupyter Notebook.                                                        |
        +---------------------+----------------------------------------------------------------------------------+
        |         openBrowser | Display url using the default browser.                                           |
        +---------------------+----------------------------------------------------------------------------------+
        |             pdfmine | Analyze PDF and extract various elements.                                        |
        +---------------------+----------------------------------------------------------------------------------+
        |  regexp-replacement | String replacement in a file using regular expression                            |
        +---------------------+----------------------------------------------------------------------------------+
        |     render-template | Render templates.                                                                |
        +---------------------+----------------------------------------------------------------------------------+
        | requirements-create | Create a ``requirements.text``                                                   |
        +---------------------+----------------------------------------------------------------------------------+
        |         revise_text | Revise word file.                                                                |
        +---------------------+----------------------------------------------------------------------------------+
        |     pycharmers-show | Show all Python-Charmers's command line programs.                                |
        +---------------------+----------------------------------------------------------------------------------+
        |            tweetile | Divide one image into three so that you can tweet beautifully.                   |
        +---------------------+----------------------------------------------------------------------------------+
        |      video_of_lyric | Create a lyric Video.                                                            |
        +---------------------+----------------------------------------------------------------------------------+
        |     video_of_typing | Create a typing video. Before using this program, please do the following things |
        +---------------------+----------------------------------------------------------------------------------+
        |           video2gif | Convert Video into Gif.                                                          |
        +---------------------+----------------------------------------------------------------------------------+
    """
    parser = argparse.ArgumentParser(prog="pycharmers-show", add_help=True)
    parser.add_argument("-H", "--head",  type=int, help="Show the first ``head`` rows for the table.")
    parser.add_argument("-W", "--width", type=int, help="Table width.")
    parser.add_argument("--description", action="store_true", help="Whether to show description or path. (default= ``False`` )")
    parser.add_argument("--tablefmt", choices=Table.SUPPORTED_FORMATS, default="github", help="The format of table.")
    parser.add_argument("--sphinx",  action="store_true", help="Whether to create for sphinx rst file.")
    parser.add_argument("--github",  action="store_true", help="Whether to create for github README.md file.")
    args = parser.parse_args(argv)

    head = args.head
    table_width = args.width
    sphinx = args.sphinx
    tablefmt = "rst" if sphinx else args.tablefmt

    paths       = []
    commands    = []
    descriptons = []
    console_scripts = get_console_scripts()
    for command, path in console_scripts:
        f,i = path.split(":")
        try:
            exec(f"from {f} import {i}")
            descriptons.append(eval(f"{i}.__doc__.split('\\n')[0]"))
        except Exception as e:
            descriptons.append(f"Could not import it [{e.__class__.__name__}] {e}")
        if args.sphinx:
            command = f":func:`{command} <{f}.{i}>`"
        elif args.github:
            command = f"[`{command}`]({BASE_URL}/{f}.html#{f}.{i})"
        commands.append(command)
        paths.append(path)

    table = Table(tablefmt=tablefmt)
    table.set_cols(values=commands, colname="command", color="GREEN")
    if args.description:
        table.set_cols(values=descriptons, colname="description", color="BLUE", align="left")
    else:
        table.set_cols(values=paths, colname="path", color="BLUE", align="left")
    table.show(head=head, table_width=table_width)

def get_console_scripts(target:str="pyproject.toml") -> List[Tuple[str,str]]:
    """Get console script list.

    Args:
        target (str, optional) : Target filename. Defaults to ``"pyproject.toml"``.

    Returns:
        List[Tuple[str,str]]: List of console scripts (``(command, path)``).
    """
    results = []
    target_path = os.path.join(REPO_DIR, target)
    if os.path.exists(target_path):
        with open(target_path, mode="r") as f: 
            lines = f.readlines()
    else:
        lines = get_soup(url=f"https://raw.githubusercontent.com/iwasakishuto/Python-Charmers/master/{target}").get_text().split("\n")
    is_cmd_scrip = False
    for line in lines:
        if line=="\n": 
            is_cmd_scrip = False
        if is_cmd_scrip:
            m = re.search(pattern=r"^(.+?)\s+=\s?\"(.+?)\"\n$", string=line)
            if m is not None:
                results.append(m.groups())
        if line.startswith("[tool.poetry.scripts]"):
            is_cmd_scrip = True
    return results
