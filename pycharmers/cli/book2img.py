# coding: utf-8
import os
import sys
import time
import json
import datetime
import argparse
import pyautogui as pygui
from pathlib import Path

from ._clipath import PYCHARMERS_CLI_BOOK2IMG_DIR
from ..utils.generic_utils import now_str
from ..utils.tkinter_utils import PortionSelector
from ..utils.monitor_utils import ProgressMonitor
from ..utils.print_utils import tabulate
from ..utils._colorings import toBLUE, toGREEN

class guiOperations():
    """Packaged Gui Operations.

    Args:
        ops (dict/str) : Operations.
    """
    HEADER_KEYS = ["description"]
    def __init__(self, ops={}):
        self.init(ops=ops)

    def init(self, ops={}):
        """Initialize the operation instance."""
        if isinstance(ops, str):
            with open(ops, mode="r") as jf:
                ops = json.load(jf)
        self.ops = ops
        for key in guiOperations.HEADER_KEYS:
            self.ops.pop(key)

    def run(self):
        """Run the packaged operations."""
        for n,op in self.ops.items():
            method = op.get("method")
            args   = op.get("args", [])
            kwargs = op.get("kwargs", {})
            exec(f"pygui.{method}(*args, **kwargs)")

def book2img(argv=sys.argv[1:]):
    """Convert Book into Sequential Images.

    Args:
        -N/--num (int)         : Number of screenshots to take.
        -I/--interval (int)    : Interval to take screenshots.
        -OP/--operations (str) : Path or Abbreviation for Operations.
        -O/--output (str)      : Path to the output directory.
        -S/--sec (int)         : Time to take a screenshot.

    Note:
        When you run from the command line, execute as follows::
        
        $ book2img -N 10 -I 1 -OP KindleApp

    .. code-block:: sh
    
        $ cat ~/.pycharmers/cli/book2img/kindleApp.json
        {
          "description": "Operations for KindleApp (Examples)",
          "1": {
            "method": "keyDown",
            "args": [
              "right"
            ],
            "kwargs": {}
          }
        }

    +--------------------------------------+
    |                Sample                |
    +======================================+
    | .. image:: _images/cli.book2img.gif  |
    +--------------------------------------+
    """
    if len(argv)==0:
        tabulate([[os.path.splitext(fn.name)[0], json.load(fn.open()).get("description", "")] for fn in Path(PYCHARMERS_CLI_BOOK2IMG_DIR).glob("*.json")], headers=["Abbreviation", "Description"])
        print(f"You can use these operations by\n{toBLUE('$ book2img -OP <Abbreviation>')}")
        sys.exit(-1)
    parser = argparse.ArgumentParser(prog="book2img", description="Convert Books to Image.", add_help=True)
    parser.add_argument("-N",  "--num",        type=int, default=1,  help="Number of screenshots to take.")
    parser.add_argument("-I",  "--interval",   type=int, default=1,  help="Interval to take screenshots.")
    parser.add_argument("-OP", "--operations", type=str, help="Path or Abbreviation for Operations.")
    parser.add_argument("-O",  "--output",     type=str, default=f"books-{now_str()}", help="Path to the output directory.")
    parser.add_argument("-S",  "--sec",        type=int, default=3, help="Time to take a screenshot")
    args = parser.parse_args(argv)
    
    num = args.num
    digit = len(str(num))
    out_dir = args.output 
    interval = args.interval
    sec = args.sec
    ops = args.operations or {}
    if (isinstance(ops, str)) and (not ops.endswith(".json")):
        ops = os.path.join(PYCHARMERS_CLI_BOOK2IMG_DIR, ops+".json")
    ops = guiOperations(ops=ops)

    ps = PortionSelector()
    ps.run()
    region = ps.get_xywh()
    print(f"Region (x,y,w,h): {toGREEN(region)}")

    os.mkdir(out_dir)
    print(f"{num} Images will saved at {toBLUE(out_dir)}")
    print(f"Screenshot will be taken in {sec} seconds.")
    time.sleep(sec)
    monitor = ProgressMonitor(max_iter=num, barname="book2img")
    for n in range(num):
        monitor.report(it=n, num_screenshots=n+1)
        ss = pygui.screenshot(region=region)
        ss.save(os.path.join(out_dir, f"img{n:>0{digit}}.png"))
        ops.run()
        time.sleep(interval)
    monitor.remove()