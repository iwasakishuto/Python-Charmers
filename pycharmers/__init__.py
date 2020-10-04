# coding: utf-8

__copyright__       = "Copyright (C) 2020 Shuto Iwasaki"
__version__         = "0.0.1"

__license__         = "MIT"
__author__          = "Shuto Iwasaki"
__author_twitter__  = "https://twitter.com/cabernet_rock"
__author_email__    = "cabernet.rock@gmail.com"
__url__             = "https://github.com/iwasakishuto/Python-Charmers"

import warnings
warnings.filterwarnings(action="ignore", category=FutureWarning)
# <frozen importlib._bootstrap>:219: FutureWarning: Passing (type, 1) or '1type' as a synonym of type is deprecated; in a future version of numpy, it will be understood as (type, (1,)) / '(1,)type'.

from . import api
from . import matplotlib
from . import opencv
from . import utils

# Import to create directories.
from .cli import _path