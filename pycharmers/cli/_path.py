#coding: utf-8
import os
from pathlib import Path

from ..utils._path import *
from ..utils._path import _makedirs, _download_sample_data

PYCHARMERS_CLI_DIR = os.path.join(PYCHARMERS_DIR, "cli") # /Users/<username>/.pycharmers/cli
_makedirs(name=PYCHARMERS_CLI_DIR)
# Directory for 'regexp_replacement.py'
PYCHARMERS_CLI_REGEXP_REPLACEMENT_DIR = os.path.join(PYCHARMERS_CLI_DIR, "regexp_replacement") # /Users/<username>/.pycharmers/cli/regexp_replace
_makedirs(name=PYCHARMERS_CLI_REGEXP_REPLACEMENT_DIR)
# Directory for 'render_templates.py'
PYCHARMERS_CLI_RENDER_TEMPLATES_DIR = os.path.join(PYCHARMERS_CLI_DIR, "render_templates") # /Users/<username>/.pycharmers/cli/render_templates
_makedirs(name=PYCHARMERS_CLI_RENDER_TEMPLATES_DIR)
