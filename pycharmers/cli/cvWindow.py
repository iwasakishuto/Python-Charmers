#coding: utf-8
import cv2
import sys
import argparse
from pycharmers.opencv import FrameWindow, RealTimeWindow

def cvWindow(argv=sys.argv[1:]):
    """Use :meth:`cvWindow <pycharmers.opencv.windows.cvWindow>` to control frames.

    Args:
        --path (str) : Path to images directory or video file.

    Note:
        When you run from the command line, execute as follows::
            
            $ cv-window path/to/video.mp4
            $ cv-window path/to/image_directories
            $ cv-window
    """
    parser = argparse.ArgumentParser(prog="render-template", description="Use cvWindow to control frame.", add_help=True)
    parser.add_argument("--path",  type=str, help="Path to image directory or video file.")
    args = parser.parse_args(argv)

    path = args.path
    if path is None:
        window = RealTimeWindow()
    else:
        window = FrameWindow(path)
    window.describe()
    while True:
        key = cv2.waitKey(1)
        is_break = window.recieveKey(key)
        if is_break:
            break