# coding: utf-8
import os
import re
import sys
import json
import math
import random
import urllib
import datetime
import warnings
import webbrowser
from pygments import highlight
from pygments.lexer import Lexer
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from pathlib import Path

from typing import Optional,List

from ._colorings import toRED, toBLUE, toGREEN, toACCENT
from ._exceptions import KeyError
from ._warnings import PythonCharmersImprementationWarning

NoneType = type(None)

def handleKeyError(lst, **kwargs):
    """Check whether all ``kwargs.values()`` in the ``lst``.

    Args:
        lst (list) : candidates.
        kwargs     : ``key`` is the varname that is easy to understand when an error occurs

    Examples:
        >>> from pycharmers.utils import handleKeyError
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

def class2str(class_):
    """Convert class to str.
    
    Args:
        class_ (class): class object
        
    Examples:
        >>> from pycharmers.utils import class2str
        >>> class2str(str)
        'str'
        >>> class2str(tuple)
        'tuple'

    """
    return re.sub(r"<class '(.*?)'>", r"\1", str(class_))

def handleTypeError(types=[], **kwargs):
    """Check whether all types of ``kwargs.values()`` match any of ``types``.

    Args:
        types (list) : Candidate types.
        kwargs       : ``key`` is the varname that is easy to understand when an error occurs

    Examples:
        >>> from pycharmers.utils import handleTypeError
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
    types = tuple([NoneType if e is None else e for e in types])
    for k,v in kwargs.items():
        if not isinstance(v, types):
            str_true_types  = ', '.join([f"'{toGREEN(class2str(t))}'" for t in types])
            srt_false_type = class2str(type(v))
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
        >>> from pycharmers.utils import str_strip
        >>> str_strip(" hoge   ")
        'hoge'
        >>> str_strip(" ho    ge   ")
        'ho ge'
        >>> str_strip("  ho    g　e")
        'ho g e'
    """
    return re.sub(pattern=r"[\s 　]+", repl=" ", string=str(string)).strip()

def now_str(tz=None, fmt="%Y-%m-%d@%H.%M.%S"):
    """Returns new datetime string representing current time local to tz under the control of an explicit format string.

    Args:
        tz (datetime.timezone) : Timezone object. If no ``tz`` is specified, uses local timezone.
        fmt (str)              : format string. See `Python Documentation <https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes>`_

    Example:
        >>> from pycharmers.utils import now_str
        >>> now_str()
        '2020-09-14@22.31.17'
        >>>now_str(fmt="%A, %d. %B %Y %I:%M%p")
        Monday, 14. September 2020 10:31PM'
        >>> now_str(tz=datetime.timezone.utc)
        '2020-09-14@13.31.17'
    """
    return datetime.datetime.now(tz=tz).strftime(fmt)

def list_transpose(lst, width):
    """ Transpose a list.

    Args:
        lst (list) : A single list.
        width (int): The width of the list.

    Notes: Perform the following conversion::

        ----------->      0, 4,  8 | 
        0, 1,  2,  3      1, 5,  9 |
        4, 5,  6,  7  ->  2, 6, 10 |
        8, 9, 10, 11      3, 7, 11 v

    Example:
        >>> from pyutils.utils import list_transpose
        >>> lst = [i for i in range(10)]
        >>> lst
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        >>> list_transpose(lst, width=3)
        [0, 3, 6, 9, 1, 4, 7, 2, 5, 8]
        >>> list_transpose(lst, width=4)
        [0, 4, 8, 1, 5, 9, 2, 6, 3, 7]
    """
    return [lst[i*width+j] for j in range(width) for i in range(len(lst)//width+1) if i*width+j < len(lst)]

def flatten_dual(lst):
    """Flatten double list.

    Args:
        lst (list): Dual list.

    Example:
        >>> from pycharmers.utils import flatten_dual
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

def calc_rectangle_size(area, w=None):
    """Calculate the lengths of the sides of the rectangle from the area and the vertical length (width).

    Args:
        area (int): The area of the rectangle.
        w (int)   : The length of the vertical line. (width) If ``w`` is None, arrange like a square.

    Returns:
        size (tuple): (w, h) 

        The tuple of the lengths of horizontal, and vertical lines. (width, height)

    Examples:
        >>> from pycharmers.utils import calc_rectangle
        >>> calc_rectangle(12, 3)
        (3, 4)
        >>> calc_rectangle(12, 18)
        (12, 1)
        >>> calc_rectangle(12, 7)
        (7, 2)

    """
    if w is None:
        w = math.ceil(math.sqrt(area))
        h = math.ceil(area/w)
    else:
        if area>=w:
            h = (area-1)//w+1
        else:
            w=area
            h=1
    return (w,h)

def readable_bytes(size, type="bytes"):
    """Unit conversion for readability.

    Args:
        size (int): File size expressed in bytes

    Examples:
        >>> from pycharmers.utils import readable_bytes
        >>> size, unit = readable_bytes(1e2)
        >>> print(f"{size:.2f}[{unit}]")
        100.00[KB]
        >>> size, unit = readable_bytes(1e5)
        >>> print(f"{size:.2f}[{unit}]")
        97.66[MB]
        >>> size, unit = readable_bytes(1e10)
        >>> print(f"{size:.2f}[{unit}]")
        9.31[GB]
    """
    for unit in ["","K","M","G"]:
        if abs(size) < 1024.0:
            break
        size /= 1024.0
        # size >> 10
    return (size, unit+"B")

def get_create(corresp_dict={}, class_=[], genre="", name="Python-Charmers"):
    """Create a get functions

    Args:
        corresp_dict (dict) : Dictionary of ``identifier`` -> instance
        class_ (list)       : The list of class names.
        genre (str)         : Genre of the class.
        name (str)          : Package name.

    Examples:
        >>> import cv2
        >>> from pycharmers.utils import get_create
        >>> all = PYCHARMERS_BACKGROUND_SUBTRACTOR_CREATORS = {
        ...     "mog" : cv2.createBackgroundSubtractorMOG2,
        ...     "knn" : cv2.createBackgroundSubtractorKNN,
        ... }
        >>> background_subtractor_create = get_create(corresp_dict=all, class_=[cv2.BackgroundSubtractor], genre="background_subtractor")
    """
    if not isinstance(class_, list): class_ = [class_]
    class_ = class_+[str]
    # Create a get function.
    def get(identifier, **kwargs):
        handleTypeError(types=class_, identifier=identifier)
        if isinstance(identifier, str):
            handleKeyError(lst=list(corresp_dict.keys()), identifier=identifier)
            instance = corresp_dict.get(identifier)(**kwargs)
        else:
            instance = identifier
        return instance
    # Set a docstrings.
    genre = genre.capitalize()
    class_str = ", ".join([class2str(e) for e in class_])
    get.__doc__ = f"""Retrieves a {name} {genre} instance.
    
    Args:
        identifier ({class_str}) : {genre} identifier, string name of a {genre}, or
                    {' '*len(class_str)}    a {name} {genre.capitalize()} instance.
    
    Returns:
        {class_[0]} : A {name} {genre} instance.    
    """
    return get

def pycat(file, head=-1, mode="r", buffering=-1, encoding=None, errors=None, newline=None, count_number=False):
    """Display the contents of the specified ``file``.

    Args:
        head (int)          :
        mode (str)          : The mode in which the file is opened. 
        buffering (int)     : Set the buffering policy.
        encoding (str)      : Name of the encoding used to encode the ``file``.
        errors (str)        : How encoding errors are to be handled.
        newline (str)       : How universal newlines works (it only applies to text mode)
        count_number (bool) : Whether to display line number.

    Examples:
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG
        >>> from pycharmers.utils import pycat
        >>> pycat(SAMPLE_LENA_IMG, mode="rb")
    """
    with open(file, mode=mode, buffering=buffering, encoding=encoding, errors=errors, newline=newline) as f:
        for i,line in enumerate(f.readlines()):
            if i==head: break
            if count_number: line = toGREEN(i) + " " + line
            print(line, end="")

def pytree(*args, pattern="**/*", disp_all=False, max_level=-1, **kwargs):
    """list contents of directories in a tree-like format.
    
    Args:
        *args/**kwargs  : Argments for ``root = Path(*args, **kwargs)``
        pattern (str)   : Argments for ``root.glob(pattern)``
        disp_all (bool) : Whether not to ignore entries starting with .
        max_level (int) : Max display depth of the directory tree.

    Examples:
        >>> from pycharmers.utils import pytree
        >>> from pycharmers.utils._path import REPO_DIR
        >>> pytree(REPO_DIR, pattern="**/*.py", max_level=3)
        /Users/iwasakishuto/Github/portfolio/Python-Charmers
        ├── build
        │   └── lib
        │       └── pycharmers
        ├── develop
        │   ├── colorbar.py
        │   ├── cvCascade.old.py
        │   ├── drawing.py
        │   ├── drawingpad.py
        │   └── monitor.py
    """
    class Tree():
        def __init__(self, filepaths=[], disp_all=False, max_level=-1):
            """Tree structure for ``pytree`` function.
            
            Args:
                filepaths (list): Filepaths which is to be printed.
                disp_all (bool) : Whether not to ignore entries starting with .
                max_level (int) : Max display depth of the directory tree.
                
            
            Examples:
                >>> tree = Tree()
                >>> tree.run(REPO_DIR)
                /Users/iwasakishuto/Github/portfolio/Python-Charmers
                ├── build
                │   └── lib
                │       └── pycharmers
                ├── develop
                │   ├── colorbar.py
                │   ├── cvCascade.old.py
                │   ├── drawing.py
                │   ├── drawingpad.py
                │   └── monitor.py   
            """
            self.filepaths = filepaths
            self.disp_all = disp_all
            self.max_level = max_level
            
        def _init(self):
            self.num_directories = 0
            self.num_files = 0

        def register(self, path):
            if os.path.isdir(path):
                self.num_directories += 1
            else:
                self.num_files += 1
            
        @staticmethod
        def pathjoin(a, *p):
            """Join two or more pathname components, inserting '/' as needed, and remove './' at the begining."""
            return re.sub(pattern=r"^\.\/", repl="", string=os.path.join(a, *p))
        
        def run(self, dirname):
            """Run ``tree`` command.
            
            Args:
                dirname: path to root directory .
            """
            self._init()
            print(toBLUE(dirname))
            self.walk(dirname=dirname, depth=1, print_prefix="")
            print(f"\n{toGREEN(self.num_directories)} directories, {toGREEN(self.num_files)} files.")

        def walk(self, dirname, depth=1, print_prefix=""):
            """Print filecontens in ``dirname`` recursively.
            
            Args:
                dirname (str)      : path to current directory.
                depth (int)        : current depth.
                print_prefix (str) : Prefix for clean output.
            """
            filenames = sorted([
                fn for fn in os.listdir(dirname) 
                if len(self.filepaths)!=0 and any([fp.startswith(self.pathjoin(dirname, fn)) for fp in self.filepaths])
            ]) 
            num_filenames = len(filenames)
            
            prefixes = ("├── ", "│   ")
            for i,fn in enumerate(filenames):
                if fn[0] == "." and (not self.disp_all): continue
                abspath = os.path.join(dirname, fn)
                # Remember the file contents.
                self.register(abspath)
                # Update prefixes for the last entries.
                if i == num_filenames-1:  prefixes=("└── ", "    ")
                # Print and walk recursively.
                if os.path.isdir(abspath): fn = toBLUE(fn)      
                print(print_prefix+prefixes[0]+fn)
                if os.path.isdir(abspath) and depth!=self.max_level: 
                    self.walk(dirname=abspath, depth=depth+1, print_prefix=print_prefix+prefixes[1])

    root = Path(*args, **kwargs)
    filepaths = [str(p) for p in root.glob(pattern)]
    tree = Tree(filepaths=filepaths, disp_all=disp_all, max_level=max_level)
    tree.run(str(root))

class formatted_enumerator():
    """Generator which yeilds elements with formatted numbers.

    Args:
        iterable (int)  : An object supporting iteration
        start (int)     : The enumerate object yields pairs containing a count (from start, which defaults to ``1``) and a value yielded by the iterable argument.

    Attributes:
        total (int) : Total number of iterable elements.
        digit (int) : Digit. It is used for formatting the index.

    Examples:
        >>> from pycharmers.utils import formatted_enumerator
        >>> gen = formatted_enumerator(["a","b","c"])
        >>> for i,d in gen:
        ...     print(i, d)
        1 a
        2 i
        3 u        
    """
    def __init__(self, iterable, start=1):
        self._i = 0
        self._iterable = iterable
        self._start = start
        self.total = len(iterable)
        self.digit = len(str(self.total))
        
    def __iter__(self):
        return self
    
    @property
    def _idx(self):
        return self._i + self._start
    
    def __next__(self):
        if self._i == self.total:
            raise StopIteration
        element = self._iterable[self._i]
        idx = f"{self._idx:>0{self.digit}}"
        self._i += 1
        return (idx, element)

def open_new_tab(url):
    """Open ``url`` in  a new page ("tab") of the default browser.

    Args:
        url (str): Local file path or url.

    Returns:
        flag (bool): Whether it was successful or not.
    
    Examples:
        >>> from pycharmers.utils import open_new_tab
        >>> open_new_tab("https://google.com")
        True
        >>> open_new_tab("sample.html")
        True
    """
    if os.path.exists(url):
        url = "file://" + os.path.abspath(url)
    return webbrowser.open_new_tab(url)

def remove_invalid_fn(fn):
    """Remove invalid file name.

    Args:
        fn (str) : filename

    Example:
        >>> from pycharmers.utils import remove_invalid_fn
        >>> remove_invalid_fn(fn="Is plasticity of synapses the mechanism of long-term memory storage?")
        'Is plasticity of synapses the mechanism of long-term memory storage'
        >>> remove_invalid_fn(fn="siDirect 2.0: updated software for designing functional siRNA with reduced seed-dependent off-target effect")
        'siDirect 2.0 updated software for designing functional siRNA with reduced seed-dependent off-target effect'
    """
    return re.sub(pattern=r'[\\\/\?\*\|<>":;]+', repl='', string=fn)

def try_wrapper(func, *args, ret_=None, msg_="", verbose_=True, **kwargs):
    """Wrap ``func(*args, **kwargs)`` with ``try-`` and ``except`` blocks.

    Args:
        func (functions) : functions.
        args (tuple)     : ``*args`` for ``func``.
        kwargs (kwargs)  : ``*kwargs`` for ``func``.
        ret_ (any)       : default ret val.
        msg_ (str)       : message to print.
        verbose_ (bool)  : Whether to print message or not. (default= ``True``) 
    
    Examples:
        >>> from pycharmers.utils import try_wrapper
        >>> ret = try_wrapper(lambda x,y: x/y, 1, 2, msg_="divide")
        Succeeded to divide
        >>> ret
        0.5
        >>> ret = try_wrapper(lambda x,y: x/y, 1, 0, msg_="divide")
        [division by zero] Failed to divide
        >>> ret is None
        True
        >>> ret = try_wrapper(lambda x,y: x/y, 1, 0, ret_=1, msg_="divide")
        >>> ret is None
        False
        >>> ret
        1
    """
    try:
        ret_ = func(*args, **kwargs)
        prefix = toGREEN("Succeeded to ")
    except Exception as e:
        prefix = toRED(f"[{str_strip(e)}] Failed to ")
    if verbose_: print(prefix + msg_)
    return ret_

def list2name(lst, how="snake"):
    """Naming convention.

    Args:
        lst (list) : List.
        how (str)  : How to convert list elements to string name.

    Examples:
        >>> from pycharmers.utils import list2name
        >>> list2name(lst=["iwasaki", "shuto"], how="camel")
        'iwasakiShuto'
        >>> list2name(lst=["iwasaki", "shuto"], how="pascal")
        'IwasakiShuto'
        >>> list2name(lst=["iwasaki", "shuto"], how="snake")
        'iwasaki_shuto'
        >>> list2name(lst=["iwasaki", "shuto"], how="kebab")
        'iwasaki-shuto'
    """
    how = how.lower()
    handleKeyError(lst=["lower camel", "camel", "upper camel", "pascal", "snake", "kebab"], how=how)
    lst = [str(e) for e in lst]
    if how in ["lower camel", "camel"]:
        lst = [e.capitalize() if i!=0 else e for i,e in enumerate(lst)]
        joint = ""
    elif how in ["upper camel", "pascal"]:
        lst = [e.capitalize() for e in lst]
        joint = ""
    elif how=="snake":
        joint = "_"
    elif how=="kebab":
        joint = "-"
    return joint.join(lst)
    
def infer_types(val, default=str):
    """Infer data types by evaluate the given source.
    
    Args:
        val (str)      : data
        default (type) : Default type.
        
    Return:
        type (type) : data type.
        
    Examples:
        >>> from pycharmers.utils import infer_types
        >>> infer_types(1)
        int
        >>> infer_types(1.1)
        float
        >>> infer_types("1e3")
        float
        >>> infer_types("Hello")
        str
    """
    t = default
    if val is not None:
        try:
            t = type(eval(str(val), {"__builtins__":None}))
        except:
            pass
    return t

def html2reStructuredText(html, base_url=""):
    """Convert html string to reStructuredText
    
    Args:
        html (str)     : html string.
        base_url (str) : base URL.
        
    Returns:
        reStructuredText (str) : reStructuredText.
        
    Examples:
        >>> from pycharmers.utils import html2reStructuredText
        >>> html2reStructuredText("<code>CODE</code>")
        ' ``CODE`` '      
        >>> html2reStructuredText(
        ...     html='<a class="reference internal" href="pycharmers.html">pycharmers package</a>',
        ...     base_url="https://iwasakishuto.github.io/Python-Charmers/"
        >>> )
        '`pycharmers package <https://iwasakishuto.github.io/Python-Charmers/pycharmers.html>`_'
    """
    html = html.replace("<code>", " ``").replace("</code>", "`` ")
    def repl(m):
        """How to replacement Match object.
        Args: 
            m (Match object) : The result of re.match() and re.search()
        """
        href,inner_text = m.groups()
        # TODO: Conbine code block and link.
        if inner_text[1:3]=="``": return inner_text
        href = urllib.parse.urljoin(base=base_url, url=href)
        return f'`{inner_text} <{href}>`_'
    return re.sub(pattern=r'<a.*?href="(.*?)">(.*?)</a>',  repl=repl, string=html)

def int2ordinal(num):
    """Convert a natural number to a ordinal number.

    Args:
        num (int): natural number

    Returns:
        str: ordinal number, like 0th, 1st, 2nd,...

    Examples:
        >>> from pycharmers.utils import int2ordinal
        >>> int2ordinal(0)
        '0th'
        >>> int2ordinal(1)
        '1st'
        >>> int2ordinal(2)
        '2nd'
        >>> int2ordinal(3)
        '3rd'
        >>> int2ordinal(4)
        '4th'
        >>> int2ordinal(11)
        '11th'
        >>> int2ordinal(21)
        '21st'
        >>> int2ordinal(111)
        '111th'
        >>> int2ordinal(121)
        '121st'
    """
    q, mod = divmod(int(num), 10)
    # if num == XXX1X, use "th"
    suffix = "th" if q % 10 == 1 else {1: "st", 2: "nd", 3: "rd"}.get(mod,"th")
    return f"{num}{suffix}"

def filenaming(name=None):
    """Avoid having the same name as an existing file.
    
    Args:
        name (str) : File name you want to name
        
    Returns:
        str : File name that is not the same name as an existing file.
        
    Examples:
        >>> import os
        >>> from pycharmers.utils import filenaming
        >>> print(os.listdir())
        ['Untitled.ipynb', 'Untitled(1).ipynb', 'Untitled(3).ipynb']
        >>> filenaming("Untitled.ipynb")
        './Untitled(2).ipynb'
        >>> filenaming("Untitled.py")
        'Untitled.py'
    """
    if name is None:
        name = "Untitled"
    dirname, basename = os.path.split(name)
    if len(dirname)==0: dirname = "."
    root, ext = os.path.splitext(basename)
    filenames_in_samedir = os.listdir(dirname)
    if basename in filenames_in_samedir:        
        existing_numbers = []
        pattern = fr"{root}\((\d+)\){ext}"
        for fn in filenames_in_samedir:
            m = re.match(pattern=pattern, string=fn)
            if m is not None:
                existing_numbers.append(int(m.group(1)))
        no = 1
        while True:
            if no not in existing_numbers:
                break
            no += 1
        basename = f"{root}({no}){ext}"
    return os.path.join(dirname, basename)

def get_pyenv(scope_variables):
    """In what environment python is running.
    
    Args:
        scope_variables (dict) : the dictionary containing the current scope's global (local) variables. ( ``globals()`` or ``locals()`` )

    Returns:
        str : wheather the environment is Jupyter Notebook or not.

    Examples:
        >>> from pycharmers.utils import get_pyenv
        >>> get_pyenv(globals())
        'Jupyter Notebook'

    TODO:
        Execute this function without arguments.
    """
    # global locals
    env = "Python shell"
    if "get_ipython" in scope_variables.keys():
        ipython_class_name = scope_variables["get_ipython"]().__class__.__name__
        if ipython_class_name == "ZMQInteractiveShell":
            env = "Jupyter Notebook"
        elif ipython_class_name == "TerminalInteractiveShell":
            env = "Ipython"
        else:
            env = "OtherShell"
    return env

def assign_trbl(data, name, default=None):
    """Return the ``name`` 's values of [``Top``, ``Right``, ``Bottom``, ``Left``] from ``data``
    
    Args:
        data (dict) : Data Dictionary.
        name (str)  : The name of the value you want to assign.
        default     : Default Value.
        
    Returns:
        tuple: Values of ``Top``, ``Right``, ``Bottom``, ``Left`` 
        
    Examples:
        >>> from pycharmers.utils import assign_trbl
        >>> assign_trbl(data={"margin": [1,2,3,4]}, name="margin")
        (1, 2, 3, 4)
        >>> assign_trbl(data={"margin": [1,2,3]}, name="margin")
        (1, 2, 3, 2)
        >>> assign_trbl(data={"margin": [1,2]}, name="margin")
        (1, 2, 1, 2)
        >>> assign_trbl(data={"margin": 1}, name="margin")
        (1, 1, 1, 1)
        >>> assign_trbl(data={"margin": 1}, name="padding", default=5)
        (5, 5, 5, 5)
    """
    vals = data.get(name, default)
    if not isinstance(vals, list):
        vals = [vals]

    if len(vals)==0:
        t = r = b = l = None
    elif  len(vals)==1:
        t = r = b = l = vals[0]
    elif len(vals)==2:
        t = b = vals[0]
        l = r = vals[1]
    elif len(vals)==3:
        t, r, b = vals
        l = r
    elif len(vals)>=4:
        t,r,b,l = vals[:4]
        
    t = data.get(f"{name}-top",    data.get(f"{name}_top",    t))
    r = data.get(f"{name}-right",  data.get(f"{name}_right",  r))
    b = data.get(f"{name}-bottom", data.get(f"{name}_bottom", b))
    l = data.get(f"{name}-left",   data.get(f"{name}_left",   l))
    return (t,r,b,l)

def relative_import(f, i, absfile, name):
    """Relative import that can be used with script files such as those executed by python commands

    Args:
        f (str)       : ``"XXX"`` of ``from XXX``
        i (str)       : ``"YYY"`` of ``import YYY``
        absfile (str) : ``os.path.abspath(__file__)``
        name (str)    : ``__name__``

    Returns:
        Object : ``exec(i)``

    Examples:
        >>> import os
        >>> from pycharmers.utils import relative_import
        >>> relative_import(f="..utils", i="LeNet", absfile=os.path.abspath(__file__), name=__name__)
    """
    global is_main_
    try:
        is_main_
    except NameError:
        is_main_ = name == "__main__"
    m = re.match(pattern=r"^(\.+)(.*)", string=f)
    if m is not None:
        num_start_period = len(m.group(1))
        if is_main_:
            for _ in range(num_start_period):
                absfile = os.path.dirname(absfile)
            g = m.group(2).split(".")
            for p in g[1:-1]:
                absfile = os.path.join(absfile, p)
            f = g[-1]
            sys.path.append(absfile)
        else:
            f = ".".join(name.split(".")[:-num_start_period]) + "." + m.group(2)
    exec(f"from {f} import {i}")
    return eval(i)

def verbose2print(verbose=True):
    """Create a simple print function based on verbose
    
    Args:
        verbose (bool) : Whether to print or not.

    Returns:
        function : Print function

    Examples:
        >>> from pycharmers.utils import verbose2print
        >>> print_verbose = verbose2print(verbose=True)
        >>> print_non_verbose = verbose2print(verbose=False)
        >>> print_verbose("Hello, world.")
        Hello, world.
        >>> print_non_verbose = verbose2print("Hello, world.")    
    """
    if verbose:
        return print
    else:
        return lambda *args,**kwargs: None

def get_random_ttfontname(random_state:Optional[int]=None) -> str:
    """Get a ttfont randomly from fonts installed on your system.

    Args:
        random_state (Optional[int], optional) : Random State. Defaults to ``None``.

    Returns:
        str: Path to the ttfont.

    Examples:
        >>> from pycharmers.utils import get_random_ttfontname
        >>> get_random_ttfontname()
        '/System/Library/Fonts/ArialHB.ttc'
        >>> get_random_ttfontname()
        '/System/Library/Fonts/AppleSDGothicNeo.ttc'
        >>> get_random_ttfontname(0)
        '/System/Library/Fonts/Palatino.ttc'
        >>> get_random_ttfontname(0)
        '/System/Library/Fonts/Palatino.ttc'
    """
    rnd = random.Random(random_state)
    if sys.platform.startswith('win'):
        font_dirs = ["C:\Windows\Fonts"]
    else:
        font_dirs = ["/System/Library/Fonts/", "/Library/Fonts/", "~/Library/Fonts/"]
    for font_dir in font_dirs + [""]:
        if os.path.exists(font_dir):
            break
        if font_dir == "":
            warnings.warn("Colud not find the font directory.", category=PythonCharmersImprementationWarning)
            return None
    return os.path.join(font_dir, rnd.choice(os.listdir(font_dir)))

def html_decode(s:str) -> str:
    """Returns the ASCII decoded version of the given HTML string. This does NOT remove normal HTML tags like ``<p>``.

    Args:
        s (str): HTML string.

    Returns:
        str: ASCII decoded string.

    Examples:
        >>> from pycharmers.utils import html_decode
        >>> html_decode('>>> print("Hello, world!")')
        '>>> print("Hello, world!")'
        >>> html_decode('&gt;&gt;&gt; print("Hello, world!")')
        '>>> print("Hello, world!")'
    """
    htmlCodes = (
        ("'", '&#39;'),
        ('"', '&quot;'),
        ('>', '&gt;'),
        ('<', '&lt;'),
        ('&', '&amp;')
    )
    for new,old in htmlCodes:
        s = s.replace(old, new)
    return s

def split_code(code:str, lexer:Lexer=PythonLexer()) -> List[List[str]]:
    """Split code based on code higlighting.

    Args:
        code (str)               : A programming code.
        lexer (Lexer, optional)  : A ``Lexer`` for a specific language. Defaults to ``PythonLexer()``.

    Returns:
        List[List[str,str]]: A dual list of code and class. ``[[code,class]]``.

    Examples:
        >>> from pycharmers.utils import split_code
        >>> splitted_code = split_code(\"\"\"
        ... >>> try:
        ... ...     from iwasakishuto import portfolio
        ... >>> except ModuleNotFoundError:
        ... ...     print(f"Nice to meet you :)")
        ... >>> portfolio.load()
        >>> \"\"\")
        >>> for code,cls in splitted_code:
        ...     print(code, end="")
    """
    code = highlight(code=code, lexer=lexer, formatter=HtmlFormatter())
    code = html_decode(code)
    data = []
    for span in code.split("</span>")[1:-1]:
        b,a = span.split("<span ")
        if len(b)>0:
            data.append([b, ""])
        m = re.search(pattern='class="(.+)">', string=a)
        data.append([a[m.end():], m.group(1)])
    return data