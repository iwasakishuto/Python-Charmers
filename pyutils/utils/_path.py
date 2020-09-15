#coding: utf-8
import os
from pathlib import Path
from ._colorings import toBLUE

__all__ = [
    "UTILS_DIR", "MODULE_DIR", "REPO_DIR", "CLI_DIR",
]

UTILS_DIR     = os.path.dirname(os.path.abspath(__file__))  # path/to/pyutils/utils
MODULE_DIR    = os.path.dirname(UTILS_DIR)                  # path/to/pyutils
REPO_DIR      = os.path.dirname(MODULE_DIR)                 # path/to/PyUtils
CLI_DIR       = os.path.join(MODULE_DIR, "cli")             # path/to/pyutils/cli
