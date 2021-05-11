"""Utility programs for `OpenCV <https://opencv.org/>`_

OpenCV (Open Source Computer Vision Library) is a library of programming functions mainly aimed at real-time computer vision. Originally developed by Intel, it was later supported by Willow Garage then Itseez (which was later acquired by Intel). The library is cross-platform and free for use under the open-source BSD license.

.. code-block:: python

    >>> from pycharmers.opencv import SAMPLE_LENA_IMG, SAMPLE_VTEST_VIDEO

+--------------------------+--------------------------------------------------+
|    variable names        |                                                  |
+==========================+==================================================+
| ``SAMPLE_LENA_IMG``      | .. image:: _images/opencv.SAMPLE_LENA_IMG.jpg    |
+--------------------------+--------------------------------------------------+
| ``SAMPLE_VTEST_VIDEO``   | .. video:: _images/opencv.SAMPLE_VTEST_VIDEO.mp4 |
|                          |    :width: 100%                                  |
|                          |    :autoplay:                                    |
+--------------------------+--------------------------------------------------+
"""

# coding: utf-8
from ._cvpath import *
from ._cvpath import save_dir_create
from . import backsub
from . import binary
from . import cvui
from . import cascade
from . import drawing
from . import editing
from . import morphology
from . import project
from . import tracking
from . import video_image_handler
from . import windows

from .backsub import background_subtractor_create

from .binary import binarizer_creator
from .binary import findBiggestContour
from .binary import reorder_contour

from .cascade import cascade_creator
from .cascade import cascade_detection_create

from .drawing import (cv2BLACK, cv2RED, cv2GREEN, cv2YELLOW, cv2BLUE, cv2MAGENTA, cv2CYAN, cv2WHITE)  
from .drawing import cv2read_mpl
from .drawing import cv2plot
from .drawing import convert_coords
from .drawing import draw_bboxes_create
from .drawing import draw_bboxes_xywh
from .drawing import draw_bboxes_ltrb
from .drawing import draw_text_with_bg
from .drawing import plot_cv2fontFaces

from .editing import cv2paste
from .editing import vconcat_resize_min
from .editing import hconcat_resize_min
from .editing import resize_aspect
from .editing import transparency
from .editing import pil2cv

from .morphology import morph_kernel_creator
from .morphology import morph_transformer_creator

from .project import cv2Project

from .tracking import tracker_create
from .tracking import BBoxLogger

from .video_image_handler import count_frame_num
from .video_image_handler import basenaming
from .video_image_handler import create_VideoWriter
from .video_image_handler import mono_frame_generator
from .video_image_handler import multi_frame_generator_concat
from .video_image_handler import multi_frame_generator_sepa
from .video_image_handler import VideoCaptureCreate

from .windows import (DEFAULT_CV_KEYS, DEFAULT_FRAME_KEYS, DEFAULT_REALTIME_KEYS, DEFAULT_TRACKING_KEYS)
from .windows import cvKeys
from .windows import cv2key2chr
from .windows import wait_for_input
from .windows import wait_for_choice
from .windows import cvWindow
from .windows import FrameWindow
from .windows import RealTimeWindow
from .windows import TrackingWindow