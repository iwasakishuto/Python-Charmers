#coding: utf-8
import os
from ..utils._path import PYCHARMERS_DIR
from ..utils._colorings import toBLUE

__all__ = ["PYCHARMERS_OPENCV_DIR", "PYCHARMERS_OPENCV_CASCADES_DIR"]

PYCHARMERS_OPENCV_DIR = os.path.join(PYCHARMERS_DIR, "opencv") # /Users/<username>/.pycharmers/opencv
if not os.path.exists(PYCHARMERS_OPENCV_DIR):
    os.mkdir(PYCHARMERS_OPENCV_DIR)
    print(f"{toBLUE(PYCHARMERS_DIR)} is created. OpenCV data will be stored here.")
PYCHARMERS_OPENCV_CASCADES_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "cascades")
if not os.path.exists(PYCHARMERS_OPENCV_CASCADES_DIR):
    os.mkdir(PYCHARMERS_OPENCV_CASCADES_DIR)
    print(f"{toBLUE(PYCHARMERS_OPENCV_CASCADES_DIR)} is created. OpenCV cascades will be stored here.")