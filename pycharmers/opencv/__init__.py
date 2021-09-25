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

from . import (
    backsub,
    binary,
    cascade,
    cvui,
    drawing,
    editing,
    morphology,
    project,
    tracking,
    video_image_handler,
    windows,
)

# coding: utf-8
from ._cvpath import *
from ._cvpath import save_dir_create
from .backsub import background_subtractor_create
from .binary import binarizer_creator, findBiggestContour, reorder_contour
from .cascade import cascade_creator, cascade_detection_create
from .drawing import (
    convert_coords,
    cv2BLACK,
    cv2BLUE,
    cv2CYAN,
    cv2GREEN,
    cv2MAGENTA,
    cv2plot,
    cv2read_mpl,
    cv2RED,
    cv2WHITE,
    cv2YELLOW,
    draw_bboxes_create,
    draw_bboxes_ltrb,
    draw_bboxes_xywh,
    draw_text_with_bg,
    plot_cv2fontFaces,
)
from .editing import (
    cv2paste,
    hconcat_resize_min,
    pil2cv,
    resize_aspect,
    transparency,
    vconcat_resize_min,
)
from .morphology import morph_kernel_creator, morph_transformer_creator
from .project import cv2Project
from .tracking import BBoxLogger, tracker_create
from .video_image_handler import (
    VideoCaptureCreate,
    VideoWriterCreate,
    basenaming,
    count_frame_num,
    mono_frame_generator,
    multi_frame_generator_concat,
    multi_frame_generator_sepa,
    videocodec2ext,
)
from .windows import (
    DEFAULT_CV_KEYS,
    DEFAULT_FRAME_KEYS,
    DEFAULT_REALTIME_KEYS,
    DEFAULT_TRACKING_KEYS,
    FrameWindow,
    RealTimeWindow,
    TrackingWindow,
    cv2key2chr,
    cvKeys,
    cvWindow,
    wait_for_choice,
    wait_for_input,
)
