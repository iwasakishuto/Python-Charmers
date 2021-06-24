#coding: utf-8
import os

from ..utils._path import _makedirs, _download_sample_data, PYCHARMERS_DIR, PYCHARMERS_ICON
from ..utils._colorings import toBLUE
from ..utils.generic_utils import now_str
from ..sdk.github import wgit

__all__ = [
    "PYCHARMERS_OPENCV_DIR", "PYCHARMERS_OPENCV_DATA_DIR",
    "PYCHARMERS_OPENCV_IMAGE_DIR", "SAMPLE_LENA_IMG",
    "PYCHARMERS_OPENCV_VIDEO_DIR", "SAMPLE_VTEST_VIDEO",
    "PYCHARMERS_OPENCV_JSON_DIR",
]

PYCHARMERS_OPENCV_DIR = os.path.join(PYCHARMERS_DIR, "opencv") # /Users/<username>/.pycharmers/opencv
_makedirs(name=PYCHARMERS_OPENCV_DIR)

PYCHARMERS_OPENCV_DATA_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "data") # /Users/<username>/.pycharmers/opencv/data
if not os.path.exists(PYCHARMERS_OPENCV_DATA_DIR):
    wgit(base_url="https://github.com/opencv/opencv/tree/master/data", base_dir=PYCHARMERS_OPENCV_DIR)

# Create Image Directory & Download sample data.
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
# Create Image Directory.
PYCHARMERS_OPENCV_JSON_DIR = os.path.join(PYCHARMERS_OPENCV_DIR, "json") # /Users/<username>/.pycharmers/opencv/json
_makedirs(name=PYCHARMERS_OPENCV_JSON_DIR)

# ===================================================== #
#  Create a directory to save data (image, video, json) #
# ===================================================== #

def save_dir_create(dirname=None, image=True, video=True, json=False):
    """Create a directory to save data (image, video, json)

    Args:
        dirname (str) : dirname for saved image or directory.
        image (bool)  : Whether you want to create a directory for image.
        video (bool)  : Whether you want to create a directory for video.
        json (bool)   : Whether you want to create a directory for json.

    Returns:
        (list)
    """
    paths = []
    if dirname is None: 
        dirname = now_str()
    if image:
        img_save_dir = os.path.join(PYCHARMERS_OPENCV_IMAGE_DIR, dirname)
        _makedirs(name=img_save_dir, msg="Images will be saved here.")
        paths.append(img_save_dir)
    if video:
        video_save_dir = os.path.join(PYCHARMERS_OPENCV_VIDEO_DIR, dirname)
        _makedirs(name=video_save_dir, msg="Videos will be saved here.")
        paths.append(video_save_dir)
    if json:
        json_save_path = os.path.join(PYCHARMERS_OPENCV_JSON_DIR, dirname+".json")
        paths.append(json_save_path)
    return paths