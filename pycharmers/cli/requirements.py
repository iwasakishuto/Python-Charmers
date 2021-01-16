#coding: utf-8
import os
import re
import sys
import argparse
from pathlib import Path

import distutils.sysconfig as sysconfig
from ..utils._colorings import toBLUE, toGREEN
from ..utils.generic_utils import flatten_dual
from ..utils.inspect_utils import get_imported_members
from ..utils.subprocess_utils import run_and_capture
from ..utils.print_utils import pretty_3quote
from ..utils._colorings import toBLUE, toGREEN, toRED

STANDARD_LIBRARIES = [fn.split(".")[0] for fn in os.listdir(sysconfig.get_python_lib(standard_lib=True))]

def requirements_create(argv=sys.argv[1:]):
    """Create a ``requirements.text``

    Args:
        path (str)  : Path to a package (module).

    Note:
        When you run from the command line, execute as follows::
        
        $ requirements-create ~/path/to/pycharmers        
    """
    parser = argparse.ArgumentParser(prog="render-template", description="Create a requirements.text", add_help=True)
    parser.add_argument("path",  type=str, help="Path to a package (module).")
    parser.add_argument("--all", action="store_true", help="Whethere print all libraries or only non-standard ones.")
    args = parser.parse_args(argv)

    only_std = not args.all
    if not only_std:
        print(*pretty_3quote(f"""
        * Standard Library    : {toGREEN('GREEN')}
        * Third-Party Library : {toBLUE('BLUE')}
        * ERROR               : {toRED('RED')}
        {"="*30}
        """))

    p = Path(args.path)
    libraries = []
    for fn in p.glob("**/*.py"):
        imported_members = get_imported_members(fn)
        imported_libraries = list(imported_members.keys()) + imported_members.get("", [])
        libraries.extend([e.split(".")[0] for e in imported_libraries])
    for lib in set(libraries):
        is_std = lib in STANDARD_LIBRARIES
        if only_std:
            if is_std:
                continue
            else:
                color = lambda x:str(x)
        else:
            color = toGREEN if is_std else toBLUE
        if len(lib)==0:
            continue
        try:
            print(color(re.sub(pattern=r"Version:\s(.*)", repl=rf"{lib}==\1", string=run_and_capture(f"pip3 show --version {lib} | grep Version"))))
        except Exception as e:
            print(toRED(e))
