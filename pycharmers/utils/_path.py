#coding: utf-8
import os
from pathlib import Path
from ._colorings import toBLUE

__all__ = [
    "UTILS_DIR", "MODULE_DIR", "REPO_DIR", "CLI_DIR", "PYCHARMERS_DIR",
]

UTILS_DIR      = os.path.dirname(os.path.abspath(__file__))           # path/to/Python-Charmers/pycharmers/utils
MODULE_DIR     = os.path.dirname(UTILS_DIR)                           # path/to/Python-Charmers/pycharmers
REPO_DIR       = os.path.dirname(MODULE_DIR)                          # path/to/Python-Charmers
CLI_DIR        = os.path.join(MODULE_DIR, "cli")                      # path/to/Python-Charmers/pycharmers/cli
PYCHARMERS_DIR = os.path.join(os.path.expanduser("~"), ".pycharmers") # /Users/<username>/.pycharmers
# Check whether uid/gid has the write access to DATADIR_BASE
if os.path.exists(PYCHARMERS_DIR) and not os.access(PYCHARMERS_DIR, os.W_OK):
    PYCHARMERS_DIR = os.path.join("/tmp", ".pycharmers")
if not os.path.exists(PYCHARMERS_DIR):
    os.mkdir(PYCHARMERS_DIR)
    print(f"{toBLUE(PYCHARMERS_DIR)} is created.")