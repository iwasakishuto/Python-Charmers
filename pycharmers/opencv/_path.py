#coding: utf-8
import os
from ..utils._path import _makedirs, _download_sample_data, PYCHARMERS_DIR
from ..utils._colorings import toBLUE

__all__ = [
    "PYCHARMERS_OPENCV_DIR", "PYCHARMERS_OPENCV_CASCADES_DIR",
    "PYCHARMERS_OPENCV_IMAGE_DIR", "SAMPLE_LENA_IMG",
    "PYCHARMERS_OPENCV_VIDEO_DIR", "SAMPLE_VTEST_VIDEO",
]

PYCHARMERS_OPENCV_DIR = os.path.join(PYCHARMERS_DIR, "opencv") # /Users/<username>/.pycharmers/opencv
_makedirs(name=PYCHARMERS_OPENCV_DIR)

PYCHARMERS_OPENCV_CASCADES_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "cascades") # /Users/<username>/.pycharmers/opencv/cascades
_makedirs(name=PYCHARMERS_OPENCV_DIR)

PYCHARMERS_OPENCV_IMAGE_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "image") # /Users/<username>/.pycharmers/opencv/image
_makedirs(name=PYCHARMERS_OPENCV_IMAGE_DIR)
SAMPLE_LENA_IMG = os.path.join(PYCHARMERS_OPENCV_IMAGE_DIR, "lena.jpg")
_download_sample_data(
    url="https://raw.githubusercontent.com/opencv/opencv/master/samples/data/lena.jpg", 
    path=SAMPLE_LENA_IMG
)
# Create Video Directory & Download sample data.
PYCHARMERS_OPENCV_VIDEO_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "video") # /Users/<username>/.pycharmers/opencv/video
_makedirs(name=PYCHARMERS_OPENCV_VIDEO_DIR)
SAMPLE_VTEST_VIDEO = os.path.join(PYCHARMERS_OPENCV_VIDEO_DIR, "vtest.avi")
_download_sample_data(
    url="https://raw.githubusercontent.com/opencv/opencv/master/samples/data/vtest.avi", 
    path=SAMPLE_VTEST_VIDEO 
)
