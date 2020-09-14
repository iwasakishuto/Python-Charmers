# coding: utf-8
import re
import json
import datetime

from ._colorings import toRED, toBLUE, toGREEN, toACCENT
from ._exceptions import KeyError

def handleKeyError(lst, **kwargs):
    """Check whether all ``kwargs.values()`` in the ``lst``.

    Args:
        lst (list) : candidates.
        kwargs     : ``key`` is the varname that is easy to understand when an error occurs

    Examples:
        >>> from pyutils.utils import handleKeyError
        >>> handleKeyError(lst=range(3), val=1)
        >>> handleKeyError(lst=range(3), val=100)
        KeyError: Please choose the argment val from ['0', '1', '2']. you chose 100
        >>> handleKeyError(lst=range(3), val1=1, val2=2)
        >>> handleKeyError(lst=range(3), val1=1, val2=100)
        KeyError: Please choose the argment val2 from ['0', '1', '2']. you chose 100

    Raise:
        KeyError: If ``kwargs.values()`` not in the ``lst``
    """
    for k,v in kwargs.items():
        if v not in lst:
            lst = ', '.join([f"'{toGREEN(e)}'" for e in lst])
            raise KeyError(f"Please choose the argment {toBLUE(k)} from [{lst}]. you chose {toRED(v)}")

def handleTypeError(types, **kwargs):
    """Check whether all types of ``kwargs.values()`` match any of ``types``.

    Args:
        lst (list) : candidate types.
        kwargs     : ``key`` is the varname that is easy to understand when an error occurs

    Examples:
        >>> from pyutils.utils import handleTypeError
        >>> handleTypeError(types=[str], val="foo")
        >>> handleTypeError(types=[str, int], val=1)
        >>> handleTypeError(types=[str, int], val=1.)
        TypeError: val must be one of ['str', 'int'], not float
        >>> handleTypeError(types=[str], val1="foo", val2="bar")
        >>> handleTypeError(types=[str, int], val1="foo", val2=1.)
        TypeError: val2 must be one of ['str', 'int'], not float

    Raise:
        TypeError: If the types of ``kwargs.values()`` are none of the ``types``
    """
    type2str = lambda t: re.sub(r"<class '(.*?)'>", r"\033[34m\1\033[0m", str(t))
    for k,v in kwargs.items():
        if not any([isinstance(v,t) for t in types]):
            str_true_types  = ', '.join([f"'{toGREEN(type2str(t))}'" for t in types])
            srt_false_type = type2str(type(v))
            if len(types)==1:
                err_msg = f"must be {str_true_types}"
            else:
                err_msg = f"must be one of [{str_true_types}]"
            raise TypeError(f"{toBLUE(k)} {err_msg}, not {toRED(srt_false_type)}")

def str_strip(string):
    """Convert all consecutive whitespace  characters to `' '` (half-width whitespace), then return a copy of the string with leading and trailing whitespace removed.

    Args:
        string (str) : string

    Example:
        >>> from pyutils.utils import str_strip
        >>> str_strip(" hoge   ")
        'hoge'
        >>> str_strip(" ho    ge   ")
        'ho ge'
        >>> str_strip("  ho    g　e")
        'ho g e'
    """
    return re.sub(pattern=r"[\s 　]+", repl=" ", string=string).strip()

def now_str(tz=None, fmt="%Y-%m-%d@%H.%M.%S"):
    """Returns new datetime string representing current time local to tz under the control of an explicit format string.

    Args:
        tz (datetime.timezone) : Timezone object. If no ``tz`` is specified, uses local timezone.
        fmt (str)              : format string. See `Python Documentation <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_

    Example:
        >>> from pyutils.utils import now_str
        >>> now_str()
        '2020-09-14@22.31.17'
        >>>now_str(fmt="%A, %d. %B %Y %I:%M%p")
        Monday, 14. September 2020 10:31PM'
        >>> now_str(tz=datetime.timezone.utc)
        '2020-09-14@13.31.17'
    """
    return datetime.datetime.now(tz=tz).strftime(fmt)

def flatten_dual(lst):
    """Flatten double list.

    Args:
        lst (list): Dual list.

    Example:
        >>> from pyutils.utils import flatten_dual
        >>> flatten_dual([[1,2,3],[4,5,6]])
        [1, 2, 3, 4, 5, 6]
        >>> flatten_dual([[[1,2,3]],[4,5,6]])
        [[1, 2, 3], 4, 5, 6]
        >>> flatten_dual(flatten_dual([[[1,2,3]],[4,5,6]]))
        TypeError: 'int' object is not iterable

    Raise:
        TypeError: If list is not a dual list.
    """
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
        h = (area-1)//w+1
    else:
        w=area
        h=1
    return (w,h)