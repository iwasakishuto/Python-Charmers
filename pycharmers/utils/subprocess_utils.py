#coding: utf-8
import re
import subprocess

def run_and_capture(cmd):
    """Run and Capture the command.

    Args:
        cmd (str/list) : A string, or a sequence of program arguments.

    Returns:
        buf (str) : Output.

    Examples:
        >>> import os
        >>> from pycharmers.utils import run_and_capture
        >>> os.getcwd() == run_and_capture("pwd")
        True
    """
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    buf = ""
    while True:
        line = proc.stdout.readline().decode("utf-8")
        buf += line
        if len(line)==0 and (proc.poll() is not None):
            break
    return buf.rstrip("\n")

def get_monitor_size():
    """Get monitor size using ``xrandr`` command. (supported only by Linux.)

    Returns:
        size (tuple) : width, height

    Examples:
        >>> from pycharmers.utils import get_monitor_size
        >>> width, height = get_monitor_size()
        >>> print(f"width  : {width}")
        width  : 1920
        >>> print(f"height : {height}")
        height : 1958
    """
    size = (-1,-1)
    m = re.search(pattern=r"(\d+)x(\d+)\s+\d+\.\d+\*", string=run_and_capture("xrandr"))
    if m is not None:
        size = tuple([int(e) for e in m.groups()])
    return size
