# coding: utf-8
from . import _colorings
from . import _exceptions
from . import _path
from . import _warnings
from . import argparse_utils
from . import color_utils
from . import download_utils
from . import generic_utils
from . import json_utils
from . import monitor_utils
from . import numpy_utils
from . import pandas_utils
from . import pil_utils
from . import print_utils
from . import soup_utils
from . import templates


from ._colorings import *
from ._exceptions import *
from ._path import *
from ._warnings import *

from .argparse_utils import ListParamProcessor
from .argparse_utils import DictParamProcessor
from .argparse_utils import KwargsParamProcessor

from .color_utils import detect_color_code_type
from .color_utils import toHEX
from .color_utils import toRGB
from .color_utils import toRGBA
from .color_utils import hex2rgb
from .color_utils import hex2rgba
from .color_utils import rgb2hex
from .color_utils import rgb2rgba
from .color_utils import rgba2hex
from .color_utils import rgba2rgb
from .color_utils import choose_text_color

from .download_utils import decide_extension
from .download_utils import download_file

from .driver_utils import DRIVER_TYPE
from .driver_utils import get_chrome_options
from .driver_utils import get_driver
from .driver_utils import try_find_element
from .driver_utils import try_find_element_click
from .driver_utils import try_find_element_send_keys
from .driver_utils import pass_forms
from .driver_utils import click
from .driver_utils import wait_until_all_elements
from .driver_utils import scrollDown

from .generic_utils import handleKeyError
from .generic_utils import handleTypeError
from .generic_utils import str_strip
from .generic_utils import now_str
from .generic_utils import class2str
from .generic_utils import list_transpose
from .generic_utils import flatten_dual
from .generic_utils import calc_rectangle_size
from .generic_utils import readable_bytes
from .generic_utils import get_create
from .generic_utils import pycat
from .generic_utils import pytree
from .generic_utils import formatted_enumerator
from .generic_utils import open_new_tab
from .generic_utils import remove_invalid_fn
from .generic_utils import try_wrapper
from .generic_utils import list2name
from .generic_utils import infer_types
from .generic_utils import html2reStructuredText
from .generic_utils import int2ordinal

from .json_utils import PythonCharmersJSONEncoder
from .json_utils import dumps_json
from .json_utils import save_json

from .monitor_utils import progress_reporthook_create
from .monitor_utils import ProgressMonitor

from .numpy_utils import take_centers
from .numpy_utils import confusion_matrix
from .numpy_utils import rotate2d

from .pandas_utils import flatten_multi_columns

from .pil_utils import pilread
from .pil_utils import roughen_img
from .pil_utils import draw_text

from .print_utils import tabulate
from .print_utils import Table
from .print_utils import format_spec_create
from .print_utils import print_func_create
from .print_utils import align_text
from .print_utils import print_dict_tree
from .print_utils import pretty_3quote
from .print_utils import visible_width
from .print_utils import strip_invisible

from .soup_utils import str2soup
from .soup_utils import split_section
from .soup_utils import group_soup_with_head
from .soup_utils import replace_soup_tag
from .soup_utils import find_target_text
from .soup_utils import find_all_target_text
from .soup_utils import find_target_id
from .soup_utils import get_soup

from .templates import render_template
from .templates import defFunction