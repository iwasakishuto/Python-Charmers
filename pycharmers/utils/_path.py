#coding: utf-8
import os
from pathlib import Path

from ._colorings import toBLUE
from .download_utils import download_file

def _makedirs(name, mode=511, msg="", verbose=True):
    """Create a directory if it does not exist.

    Args:
        name (str) : path/to/directory.
        mode (int) : The mode argument is ignored on Windows.
        msg (str)  : Add info

    Examples:
        >>> from pycharmers.utils import _makedirs
        >>> _makedirs(name="path/to/dirname")
        path/to/dirname is created.
    """
    if not os.path.exists(name):
        os.makedirs(name=name, mode=mode)
        if verbose: print(f"{toBLUE(name)} is created. {msg}")
  
def _download_sample_data(url, path, msg=""):
    """Download sample data.
    Args:
        url (str)  : File URL.
        path (str) : path/to/downloaded_file
        msg (str)  : Add info

    Examples:
        >>> from pycharmers.utils import _download_sample_data
        >>> from pycharmers.utils import SAMPLE_LENA_IMG
        >>> _download_sample_data(
        ...     url="https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg", 
        ...     path=SAMPLE_LENA_IMG
        >>> )
        Download a file from https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg
                    * Content-Encoding : None
                    * Content-Length   : (89.662109375, 'MB')
                    * Content-Type     : image/jpeg
                    * Save Destination : /Users/iwasakishuto/.pycharmers/opencv/image/lena.jpg
        lena.jpg	100.0%[####################] 0.0[s] 4.9[GB/s]	eta -0.0[s]
        /Users/iwasakishuto/.pycharmers/opencv/image/lena.jpg is downloaded. 
    """
    if not os.path.exists(path):
        download_file(url, dirname=".", path=path, bar_width=20, verbose=True)
        print(f"{toBLUE(path)} is downloaded. {msg}")

__all__ = [
    "_makedirs", "_download_sample_data",
    "UTILS_DIR", "MODULE_DIR", "TEMPLATES_DIR", "REPO_DIR", "CLI_DIR", "PYCHARMERS_DIR", "DOTENV_PATH",
    "PYCHARMERS_HTML_DIR", "PYCHARMERS_ICON"
]

UTILS_DIR       = os.path.dirname(os.path.abspath(__file__))           # path/to/Python-Charmers/pycharmers/utils
MODULE_DIR      = os.path.dirname(UTILS_DIR)                           # path/to/Python-Charmers/pycharmers
TEMPLATES_DIR   = os.path.join(MODULE_DIR, "templates")                # path/to/Python-Charmers/pycharmers/templates
REPO_DIR        = os.path.dirname(MODULE_DIR)                          # path/to/Python-Charmers
CLI_DIR         = os.path.join(MODULE_DIR, "cli")                      # path/to/Python-Charmers/pycharmers/cli
PYCHARMERS_DIR  = os.path.join(os.path.expanduser("~"), ".pycharmers") # /Users/<username>/.pycharmers
# Check whether uid/gid has the write access to DATADIR_BASE
if os.path.exists(PYCHARMERS_DIR) and not os.access(PYCHARMERS_DIR, os.W_OK):
    PYCHARMERS_DIR = os.path.join("/tmp", ".pycharmers")
_makedirs(name=PYCHARMERS_DIR)
# Dot Environment Path.
DOTENV_PATH     = os.path.join(PYCHARMERS_DIR, ".env")                 # /Users/<username>/.pycharmers/.env
if not os.path.exists(DOTENV_PATH):
    Path(DOTENV_PATH).touch()
    print(f"{toBLUE(DOTENV_PATH)} is created. Environment variables should be stored here.")
# HTML directory
PYCHARMERS_HTML_DIR = os.path.join(PYCHARMERS_DIR, "html") # /Users/<username>/.pycharmers/html
_makedirs(name=PYCHARMERS_HTML_DIR)
# Icon 
PYCHARMERS_ICON = os.path.join(os.path.join(PYCHARMERS_DIR, "icon.png")) # /Users/<username>/.pycharmers/icon.png
_download_sample_data(
    url="https://github.com/iwasakishuto/Python-Charmers/blob/master/image/favicon.png?raw=true", 
    path=PYCHARMERS_ICON,
)