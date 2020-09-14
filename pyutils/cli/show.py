#coding: utf-8
import os
import sys
import argparse
from ..utils import REPO_DIR, CLI_DIR, toBLUE, toGREEN

sys.path.append(REPO_DIR)
from setup import CONSOLE_SCRIPTS

def show(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog="pyutils-show", add_help=True)
    parser.add_argument("", type=str, help="URL of a page you want to create a pdf.")
    args = parser.parse_args(argv)

    print(f"Display All Supported Commands")
    for console_script in CONSOLE_SCRIPTS:
        print(console_script.split("="))