# coding: utf-8
"""

TODO:
    Translate from "module name" to "package name". 
"""

import re
import inspect
import pathlib
from collections import defaultdict

from .generic_utils import str_strip, flatten_dual

def get_defined_members(obj, predicate=lambda x: inspect.isfunction(x) or inspect.isclass(x)):
    """Get only defined members. 
    
    Args:
        obj (object)         : module.
        predicate (callable) : Only return members that satisfy a given ``predicate`` .

    Returns:
        dict : ``{"member name" : "member object"}``

    Examples:
        >>> from pycharmers.utils import inspect_utils, get_defined_members
        >>> get_defined_members(inspect_utils)
        {
            'get_defined_members': <function pycharmers.utils.inspect_utils.get_defined_members(obj, predicate=<function <lambda> at 0x14227fca0>)>,
            'get_imported_members': <function pycharmers.utils.inspect_utils.get_imported_members(obj)>
        }
    """
    imported_members = flatten_dual(get_imported_members(obj).values())
    return {name:member for name,member in inspect.getmembers(obj, predicate=predicate) if name not in imported_members}

def get_imported_members(obj):
    """Get import members.

    Args:
        obj (str/object) : module or path to files.

    Returns 
        dict : ``{ "module" : ["import members"]}``

    Examples:
        >>> from pycharmers.utils import inspect_utils, get_imported_members, dumps_json
        >>> print(dumps_json(obj=get_imported_members(inspect_utils)))
        {
            "": [
                "re",
                "inspect"
            ],
            "collections": [
                "defaultdict"
            ],
            ".generic_utils": [
                "str_strip",
                "flatten_dual"
            ]
        }
    """
    if isinstance(obj, pathlib.PosixPath):
        obj = str(obj)
    elif not isinstance(obj, str):
        obj = inspect.getfile(obj)
    with open(obj, mode="r") as f:
        file_contents = "".join(f.readlines())
    imported_members = defaultdict(list)
    for m,v_wb,v_nb in re.findall(pattern=r"(?:^|(?<=\n))(?:from\s+(.+?)\s+)?import\s+(?:\(((?:.|\s)*?)\)|((?:(?<!\()(?:.|\s))*?))\n", string=file_contents):
        imported_members[m].extend([str_strip(v) for v in (v_wb + v_nb).split(" as ")[0].split(",")])
    return imported_members

    