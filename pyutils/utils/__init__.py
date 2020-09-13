# coding: utf-8
from ._exceptions import *
from ._path import *
from ._warnings import *
from . import argparse_utils
from . import color_utils
from . import generic_utils
from . import monitor_utils
from . import print_utils

from .argparse_utils import MonoParamProcessor

from .color_utils import *

from .generic_utils import handleKeyError
from .generic_utils import handleTypeError
from .generic_utils import str_strip
from .generic_utils import now_str
from .generic_utils import flatten_dual
from .generic_utils import calc_rectangle_size

from .monitor_utils import ProgressMonitor

from .numpy_utils import take_a_between
from .numpy_utils import confusion_matrix

from .print_utils import (toGRAY, toRED, toGREEN, toYELLOW, toBLUE, toPURPLE, toCYAN,
                          toWHITE, toREVERSE, toACCENT, toFLASH, toRED_FLASH)
