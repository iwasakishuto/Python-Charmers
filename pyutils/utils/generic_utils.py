# coding: utf-8
import re
import json
import datetime

from .print_utils import toRED, toBLUE, toGREEN, toACCENT
from ._exceptions import KeyError

def handleKeyError(lst, **kwargs):
    k,v = kwargs.popitem()
    if v not in lst:
        lst = ', '.join([f"'{toGREEN(e)}'" for e in lst])
        raise KeyError(f"Please choose the argment {toBLUE(k)} from [{lst}]. you chose {toRED(v)}")

def handleTypeError(types, **kwargs):
    type2str = lambda t: re.sub(r"<class '(.*?)'>", r"\033[34m\1\033[0m", str(t))
    k,v = kwargs.popitem()
    if not any([isinstance(v,t) for t in types]):
        str_true_types  = ', '.join([f"'{toGREEN(type2str(t))}'" for t in types])
        srt_false_type = type2str(type(v))
        if len(types)==1:
            err_msg = f"must be {str_true_types}"
        else:
            err_msg = f"must be one of [{str_true_types}]"
        raise TypeError(f"{toBLUE(k)} {err_msg}, not {toRED(srt_false_type)}")

def str_strip(string):
    return re.sub(pattern=r"[\s 　]+", repl=" ", string=string).strip()

def now_str(fmt="%Y-%m-%d@%H.%M.%S"):
    return datetime.datetime.now().strftime(fmt)

def flatten_dual(lst):
    return [element for sublist in lst for element in sublist]

def calc_rectangle_size(area, w):
    """Calculate the lengths of the sides of the rectangle from the area and the vertical length (width).

    Args:
        area (int): The area of the rectangle.
        w (int)   : The length of the vertical line. (width)

    Returns:
        size (tuple): (w, h) 

        The tuple of the lengths of horizontal, and vertical lines. (width, height)

    Examples:
        >>> calc_rectangle(12, 3)
        (3, 4)
        >>> calc_rectangle(12, 18)
        (12, 1)
        >>> calc_rectangle(12, 7)
        (7, 2)

    """
    if area>=w:
        h = (area-1)//v+1
    else:
        w=area
        h=1
    return (w,h)