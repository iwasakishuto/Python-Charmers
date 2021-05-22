# coding: utf-8
import re
import wcwidth
import numpy as np

from ._colorings import _toCOLOR_create
from .generic_utils import handleKeyError, handleTypeError

f_aligns           = ["<", ">", "=", "^", "left", "right", "center"]
f_signs            = ["+", "-", " ", ""]
f_grouping_options = ["_", ",", ""]
f_types            = ["b", "c", "d", "e", "E", "f", "F", "g", "G", "n", "o", "s", "x", "X", "%"]
invisible_codes       = re.compile(r"\x1b\[\d+[;\d]*m|\x1b\[\d*\;\d*\;\d*m")  # ANSI color codes
invisible_codes_bytes = re.compile(b"\x1b\\[\\d+\\[;\\d]*m|\x1b\\[\\d*;\\d*;\\d*m")

def format_spec_create(align=">", sign="", zero_padding=False, width=0, grouping_option="", fmt=""):
    """Create a function which returns a formatted text.

    ``format_spec = [[fill]align][sign][#][0][width][grouping_option][.precision][type]``

    Args:
        width
        align (str)           : [[fill]align] One of ``["<", ">", "=", "^"]``
        sign (str)            : [sign] One of ``["+", "-", " ", ""]``
        zero_padding (bool)   : [0]
        width (int)           : [width]
        grouping_option (str) : [grouping_option] One of ``["_", ",", ""]``
        fmt (str)             : [.precision][type] One of ``["b", "c", "d", "e", "E", "f", "F", "g", "G", "n", "o", "s", "x", "X", "%"]``

    Returns:
        format_spec: lambda (`<function __main__.<lambda>(fill)>`)
        
    References:
        - `Python Source Code <https://github.com/python/cpython/blob/3.8/Lib/string.py>`_ 
        - `Python Documentation <https://docs.python.org/3/library/string.html#format-specification-mini-language>`_

    Examples:
        >>> from pycharmers.utils import format_spec_create
        >>> format_spec = format_spec_create(width=10, align="^")
        >>> format_spec("hoge")
        '   hoge   '
        >>> format_spec = format_spec_create(align="<", fmt=".1%")
        >>> format_spec(1/3)
        '33.3%'
        >>> format_spec = format_spec_create(align=">", zero_padding=True, fmt="b")
        >>> format_spec(20)
        '10100'
    """
    handleKeyError(lst=f_aligns, align=align)
    handleKeyError(lst=f_signs,  sign=sign)
    handleKeyError(lst=f_grouping_options, grouping_option=grouping_option)
    if len(fmt)>0:
        handleKeyError(lst=f_types, fmt=fmt[-1])
    zero = "0" if zero_padding else ""
    handleTypeError(types=[int], width=width)
    return lambda fill : align_text(f"{fill:{sign}{zero}{grouping_option}{fmt}}", align=align, width=width)

def align_text(string, align="left", width=0):
    """Align text

    Args:
        string (str) : Strig.
        align (str)  : How to align the string.
        width (int)  : Width.

    Returns:
        string (str) : Aligned text.

    Examples:
        >>> from pycharmers.utils import align_text, toBLUE
        >>> print(align_text("Hello world!", align=">", width=15))
           Hello world!
        >>> print(align_text(toBLUE("Hello world!"), align=">", width=15))
           \x1b[34mHello world!\x1b[0m
    """
    handleKeyError(lst=f_aligns, align=align)
    s_width = visible_width(string)
    pad = width - s_width
    prefix, suffix = {
        "<"     : ("",           " "*pad),
        ">"     : (" "*pad,      ""),
        "^"     : (" "*(pad//2), " "*(pad-pad//2)),    
        "="     : (" "*(pad//2), " "*(pad-pad//2)),    
        "left"  : ("",           " "*pad),
        "right" : ("",           " "*pad),
        "center": (" "*(pad//2), " "*(pad-pad//2)),   
    }[align]
    return prefix + string + suffix

def print_func_create(align=">", sign="", zero_padding=False, width=0, 
                      grouping_option="", fmt="", color="", is_bg=False,
                      left_side_bar="", right_side_bar="",
                      left_margin=0, right_margin=0, end="\n"):
    """Create a function which prints a formatted text. Please see also the function `format_spec_create`.
    
    Args:
        color (str)                : color.
        is_bg (bool)               : Whether to add color to the background or not.
        left(right)_side_bar (str) : Characters to output to the Left/Right side.
        left(right)_margin (int)   : Left/Right side margin
        end (str)                  : string appended after the last value, default a newline.
    
    Returns:
        print_func: Function that can be used like print

    Examples:
        >>> from pycharmers.utils import print_func_create
        >>> print_func = print_func_create(width=8, align="^", left_side_bar="[", right_side_bar="]")
        >>> print_func("hoge")
        [  hoge  ]
        >>> print_func = print_func_create(align="<", left_side_bar="$ ")
        >>> print_func("git clone https://github.com/iwasakishuto/Python-utils.git")
        $ git clone https://github.com/iwasakishuto/Python-utils.git
        >>> print_func("cd Python-utils")
        $ cd Python-utils
        >>> print_func("sudo python setup.py install")
        $ sudo python setup.py install
    """
    format_spec = format_spec_create(
        align=align, sign=sign, zero_padding=zero_padding,
        width=width, grouping_option=grouping_option, fmt=fmt
    )
    toCOLOR = _toCOLOR_create(color)
    def print_func(fill):
        info  = f"{left_side_bar}{' '*left_margin}"
        info += toCOLOR(format_spec(fill), is_bg=is_bg)
        info += f"{' '*right_margin}{right_side_bar}"
        print(info, end=end)
    return print_func

class Table():
    """Create a beautiful table and show.

    Args:
        tablefmt (str)        : The format of tabel.
        enable_colspan (bool) : Whether to enable ``colspan`` or not.
        mincolwidth (int)     : The minimum width of each column.

    Properties:
        ncols(int) : the number of columns.

    Methods:
        set_cols : Set values to a table.
        show     : Show a table.

    Examples:
        >>> from pycharmers.utils import Table, toBLUE
        >>> table = Table(enable_colspan=True)
        >>> table.set_cols([1,2,""], colname="id")
        >>> table.set_cols([toBLUE("abc"), "", "de"], color="GREEN")
        >>> table.show()
        +----+-------+
        | id | col.2 |
        +====+=======+
        |  1 |   \x1b[34mabc\x1b[0m |
        +----+       +
        |  2 |       |
        +    +-------+
        |    |    \x1b[32mde\x1b[0m |
        +----+-------+
    """
    SUPPORTED_FORMATS = ["github", "rst"]
    def __init__(self, tablefmt="rst", enable_colspan=True, mincolwidth=3):
        handleKeyError(lst=Table.SUPPORTED_FORMATS, tablefmt=tablefmt)
        self.cols = {}
        self.table_width = 1
        self.head = 0
        self.tablefmt = tablefmt
        self.enable_colspan = enable_colspan
        self.mincolwidth = mincolwidth
    
    @property
    def ncols(self):
        return len(self.cols)

    def _print_thead(self, vedge="|"):
        """Print headers.

        Args:
            vedge (str) : The symbol of the vertical edge.
        """
        for colname, options in self.cols.items():
            print(vedge, end="")
            options["print_title"](colname)
        print(vedge)

    def _print_border(self, vertex="+", hedge="-", alignmark=None, is_next_has_vals=None):
        """Print border.

        Args:
            vertex (str)            : The symbol of vertex.
            hedge (str)             : The symbol of the horizontal edge.
            alignmark (str)         : The symbol which implies the alignment.
            is_next_has_vals (list) : is each next column has the value or not.
        """
        if alignmark is None:
            alignmark=hedge
        is_next_has_vals = is_next_has_vals or [True]*self.ncols
        border = vertex
        for (colname, options),is_next_has_val in zip(self.cols.items(),is_next_has_vals):
            if (not self.enable_colspan) or is_next_has_val:
                edge = alignmark + hedge*(options["colwidth"]-2) + alignmark
                align = options["align"]
                if align=="right":
                    edge = hedge + edge[1:]
                elif align == "left":
                    edge = edge[:-1] + hedge
                border += edge + vertex
            else:
                border += " "*options["colwidth"] + vertex
        print(border)

    def _print_tbody(self, head=None, vedge="|", hedge="-", need_border=True):
        """Print Values.

        Args:
            head (int)         : How many lines to display.
            vedge (str)        : The symbol of the vertical edge.
            hedge (str)        : The symbol of the horizontal edge.
            need_border (bool) : Whether the border between tbodys are needed or not.
        """
        if head is None: head=self.head
        loop_not_last = True
        for i in range(head):
            if i+1==head: 
                loop_not_last=False
            is_next_has_vals=[]
            for colname, options in self.cols.items():
                print(vedge, end="")
                values = options["values"]
                options["print_values"](str(values[i]))
                if loop_not_last: 
                    is_next_has_vals.append(len(str(values[i+1]))!=0)
            print(vedge)
            if need_border and loop_not_last:
                self._print_border(hedge=hedge, is_next_has_vals=is_next_has_vals)

    def show(self, head=None, table_width=None, tablefmt=None):
        """Show a table
        
        Args:
            head (str)        : Show the first ``head`` rows for the table. 
            table_width (int) : The table width.
        """
        tablefmt = tablefmt or self.tablefmt
        handleKeyError(lst=Table.SUPPORTED_FORMATS, tablefmt=tablefmt)
        show_func = getattr(self, f"show_{tablefmt}")
        show_func(head=head, table_width=table_width)

    def show_github(self, head=None, table_width=None):
        """Show a table with github format.
        
        Args:
            head (str)        : Show the first ``head`` rows for the table. 
            table_width (int) : The table width.

        Examples:
            >>> from pycharmers.utils import Table
            >>> table = Table()
            >>> table.set_cols(values=range(3), colname="Number")
            >>> table.set_cols(values=["iwa", "saki", "shuto"], colname="Name")
            >>> table.show_github()
            | Number | Name  |
            |:------:|:-----:|
            |      0 |   iwa |
            |      1 |  saki |
            |      2 | shuto |
        """
        self._print_thead(vedge="|")
        self._print_border(vertex="|", hedge="-", alignmark=":", is_next_has_vals=None)
        self._print_tbody(head=head, hedge="-", need_border=False)

    def show_rst(self, head=None, table_width=None):
        """Show a table with rst format.
        
        Args:
            head (str)        : Show the first ``head`` rows for the table. 
            table_width (int) : The table width.

        Examples:
            >>> from pycharmers.utils import Table
            >>> table = Table()
            >>> table.set_cols(values=range(3), colname="Number")
            >>> table.set_cols(values=["iwa", "saki", "shuto"], colname="Name")
            >>> table.show_rst()
            +--------+-------+
            | Number | Name  |
            +========+=======+
            |      0 |   iwa |
            +--------+-------+
            |      1 |  saki |
            +--------+-------+
            |      2 | shuto |
            +--------+-------+
        """
        self._print_border(vertex="+", hedge="-", is_next_has_vals=None)
        self._print_thead(vedge="|")
        self._print_border(vertex="+", hedge="=", is_next_has_vals=None)
        self._print_tbody(head=head, hedge="-", need_border=True)
        self._print_border(vertex="+", hedge="-", is_next_has_vals=None)

    def set_cols(self, values, colname=None, width=0, align=">", sign="",
                 zero_padding=False, grouping_option="", fmt="", color="",
                 left_margin=1, right_margin=1):
        """Set values to a table.
        
        Args:
            values (array) : The array-like data.
            colname (str)  : The colname for ``values``.
            **kwargs       : See also ``print_func_create``
        """
        colname = colname or f"col.{self.ncols+1}"
        title_width = visible_width(str(colname))
        format_spec = format_spec_create(
            width=width, align=align, sign=sign, zero_padding=zero_padding,
            grouping_option=grouping_option, fmt=fmt
        )
        width = max(max([visible_width(format_spec(v)) for v in values]), title_width)
        self.table_width += width + left_margin + right_margin + 1

        print_title = print_func_create(
            align="center", sign="", zero_padding=False, width=width, 
            grouping_option="", fmt="", color="",
            left_side_bar="", right_side_bar="", end="",
            left_margin=left_margin, right_margin=right_margin,
        )
        print_values = print_func_create(
            align=align, sign=sign, zero_padding=zero_padding, width=width,
            grouping_option=grouping_option, fmt=fmt, color=color,
            left_side_bar="", right_side_bar="", end="",
            left_margin=left_margin, right_margin=right_margin,
        )
        self.cols.update({
            colname: {
                "print_values" : print_values,
                "print_title"  : print_title,
                "values"       : values,
                "colwidth"     : max(width+left_margin+right_margin, self.mincolwidth),
                "align"        : align,
            }
        })
        nrows = len(values)
        if self.head==0 or nrows < self.head:
            self.head = nrows

def tabulate(tabular_data=[[]], headers=[], tablefmt="rst", aligns="left"):
    """Format a fixed width table for pretty printing.
    
    Args:
        tabular_data (list) : tbody contents. Must be a dual list.
        headers (list)      : thead contents.
        tablefmt (str)      : Table format for :py:class:`Table <pycharmers.utils.print_utils.Table>`
        aligns (list)       : How to align values in each col.

    Examples:
        >>> from pycharmers.utils import tabulate
        >>> tabulate([[i*j for i in range(1,4)] for j in range(1,4)])
        +-------+-------+-------+
        | col.1 | col.2 | col.3 |
        +=======+=======+=======+
        |     1 |     2 |     3 |
        +-------+-------+-------+
        |     2 |     4 |     6 |
        +-------+-------+-------+
        |     3 |     6 |     9 |
        +-------+-------+-------+
    """
    ncols = len(tabular_data[0])
    nheaders = len(headers)
    headers += [None] * (ncols-nheaders)
    table = Table(tablefmt=tablefmt)
    if isinstance(aligns, str):
        aligns = [aligns]*len(headers)
    for col_value, header,align in zip(np.array(tabular_data).T, headers, aligns):
        table.set_cols(values=col_value, colname=header, align=align)
    table.show()

def print_dict_tree(dictionary, indent=4, rank=0, marks=["-", "*", "#"]):
    """Print Dictionary as a Tree.

    Args:
        dictionary (dict) : An input dictionary.
        indent (int)      : Indent.
        rank (int)        : A current rank.
        marks (list)      : List mark types.

    Examples:
        >>> from pycharmers.utils import print_dict_tree
        >>> print_dict_tree({"a": 0, "b": 1})
        - a: 0
        - b: 1
        >>> print_dict_tree({"a": 0, "b": {"b1": 1, "b2": 2}})
        - a: 0
        - b: 
          * b1: 1
          * b2: 2
        >>> print_dict_tree({"a": 0, "b": {"b1": 1, "b2": {"b21": 0, "b22": 1}}, "c": 3})
        - a: 0
        - b: 
          * b1: 1
          * b2: 
            # b21: 0
            # b22: 1
        - c: 3
    """
    if hasattr(dictionary, "items"):
        for k,v in dictionary.items():
            if hasattr(v, "items"):
                print(f"{' '*indent*rank}{marks[rank%len(marks)]} {k}: ")
                print_dict_tree(dictionary=v, indent=indent, rank=rank+1, marks=marks)
            else:
                print(f"{' '*indent*rank}{marks[rank%len(marks)]} {k}: {v}")

def pretty_3quote(*value, indent=0):
    """pretty 3 quote string.
    
    Args:
        indent (int)  : If indent is a non-negative integer, then multiple lines will be pretty-printed with that indent level.
        
    Examples:
        >>> from pycharmers.utils import pretty_3quote
        >>> print(*pretty_3quote(\"\"\"
        ...     When I was 17, I read a quote that went something like: 
        ...     “If you live each day as if it was your last, someday you’ll most certainly be right.”
        ...     It made an impression on me, and since then, for the past 33 years, 
        >>> \"\"\"))
        When I was 17, I read a quote that went something like: 
        “If you live each day as if it was your last, someday you’ll most certainly be right.”
        It made an impression on me, and since then, for the past 33 years, 
    """
    return [re.sub(pattern=r"\n\s+", repl=r"\n"+r" "*indent, string=val).strip("\n") for val in value]

def strip_invisible(s):
    """Remove invisible ANSI color codes.
    
    Args:
        s (str) : String.

    Returns:
        s (str) : String with invisible code removed.

    Examples:
        >>> from pycharmers.utils import strip_invisible, toBLUE
        >>> strip_invisible("\x1b[31mhello\x1b[0m")
        'hello'
        >>> strip_invisible(toBLUE("hello"))
        'hello'
        >>> strip_invisible("hello")
        'hello'
    """
    if isinstance(s, str):
        return re.sub(pattern=invisible_codes, repl="", string=s)
    elif isinstance(s, bytes): 
        return re.sub(pattern=invisible_codes_bytes, repl="", string=s)

def visible_width(s):
    """Visible width of a printed string. ANSI color codes are removed.

    Args:
        s (str) : String.

    Returns:
        width (int) : Visible width

    Examples:
        >>> from pycharmers.utils import visible_width, toBLUE
        >>> visible_width(toBLUE("hello"))
        5
        >>> visible_width("こんにちは")
        10
        >>> visible_width("hello 世界。")
        12
    """
    if isinstance(s, str) or isinstance(s, bytes):
        return wcwidth.wcswidth(strip_invisible(s))
    else:
        return wcwidth.wcswidth(str(s))

def str2pyexample(string):
    """Create a python example code.
    
    Args:
        string (str) : A string of Python Example Code.
        
    Examples:
        >>> from pycharmers.utils import str2pyexample
        >>> WINDOW_NAME = "string2python"
        >>> str2pyexample(\"\"\"
        ... import cv2
        ... import numpy as np
        ... frame = np.zeros(shape=(50, 100, 3), dtype=np.uint8)
        ... while (True):
        ...     cv2.imshow(WINDOW_NAME, frame)
        ...     if cv2.waitKey(0) == 27: break
        ... cv2.destroyAllWindows()
        ... \"\"\")
        >>> import cv2
        >>> import numpy as np
        >>> frame = np.zeros(shape=(50, 100, 3), dtype=np.uint8)
        >>> while (True):
        ...     cv2.imshow(WINDOW_NAME, frame)
        ...     if cv2.waitKey(0) == 27: break
        >>> cv2.destroyAllWindows()
    
    """
    for s in string.strip().split("\n"):
        if len(s)==0 or s[0] == " ":
            prefix = "..."
        else:
            prefix = ">>>"
        print(f"{prefix} {s}")