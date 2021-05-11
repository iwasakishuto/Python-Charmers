#coding: utf-8
import os
import sys
import argparse
import webbrowser

from ..utils._colorings import toBLUE, toGREEN
from ..utils.print_utils import pretty_3quote

def openBrowser(argv=sys.argv[1:]):
    """Display url using the default browser.

    Args:
        url (str)           : URL
        -N/--num (int)      : The number of pages.
        --new-window (bool) : Path to the output image.
        --new-tab (bool)    : Enter a size separated by a comma ( ``width`` , ``height`` )
        --not-raise (bool)  : How many times gif image loops.

    Note:
        When you run from the command line, execute as follows::
        
        $ openBrowser "https://iwasakishuto.github.io/" --N 3
    """
    parser = argparse.ArgumentParser(prog="video2gif", description="Convert Video into Gif.", add_help=True)
    parser.add_argument("url",          type=str, help="URL to open.")
    parser.add_argument("-N", "--num",  type=int, help="The number of pages.", default=1)
    parser.add_argument("--new-window", action="store_true", help="Open URL in a new brower window.")
    parser.add_argument("--new-tab",    action="store_true", help="Open URL in a new brower page ('tab')")
    parser.add_argument("--not-raise",  action="store_true", help="If True, not raises the window.")
    args = parser.parse_args()

    url = args.url
    N = args.num
    new = 1 if args.new_window else 2 if args.new_tab else 0
    autoraise = not args.not_raise    
    print(f"Open {toBLUE(url)} in {toGREEN(N)} times.")
    
    for n in range(N):
        webbrowser.open(url=url, new=new, autoraise=autoraise)