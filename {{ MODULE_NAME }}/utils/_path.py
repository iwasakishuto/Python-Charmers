#coding: utf-8
import os
from pathlib import Path
from .coloring_utils  import toBLUE

__all__ = [
    "UTILS_DIR", "MODULE_DIR", "REPO_DIR",
]

UTILS_DIR     = os.path.dirname(os.path.abspath(__file__))  # path/to/{{ MODULE_NAME }}/utils
MODULE_DIR    = os.path.dirname(UTILS_DIR)                  # path/to/{{ MODULE_NAME }}
REPO_DIR      = os.path.dirname(MODULE_DIR)                 # path/to/{{ REPOSITORY_NAME }}
