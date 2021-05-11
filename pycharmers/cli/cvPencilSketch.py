# coding: utf-8
import cv2
import sys
import argparse
import numpy as np
from ..utils import cv2ArgumentParser
from ..opencv import cvui, cv2Project
from ..opencv.binary import binarizer_creator, OPENCV_BINARYZATIONS

def cvPencilSketch(argv=sys.argv[1:]):
    """Convert the image like a pencil drawing.

    1. Convert to Gray Scale.
    2. Blur (Using Median Blur ``cv2.medianBlur`` )
    3. Laplacian ( ``cv2.Laplacian`` )
    4. Binarization.
    5. Morphological Transformations.
    
    Args:
        path (str)   : Path to image.

    Note:
        When you run from the command line, execute as follows::
        
        $ cv-pencil-sketch --path path/to/sample.png   

    +--------------------------------------------+
    |                Sample                      |
    +============================================+
    | .. image:: _images/cli.cvPencilSketch.gif  |
    +--------------------------------------------+
    """
    parser = cv2ArgumentParser(prog="cv-pencil-sketch", description="Convert the image like a pencil drawing.", add_help=True)
    args = parser.parse_args(argv)
    project = cv2Project(args=args)

    labels = ["Original", "Gray", "Blur", "Laplacian", "Binarization", "Morphological"]
    states = [i==0 for i in range(len(labels))]
    bi_labels = list(OPENCV_BINARYZATIONS.keys())
    bi_states = [i==0 for i in range(len(bi_labels))]
    bi_thresholds = [127]
    bi_blockSizes = [11] 
    bi_consts = [2]
    lap_ksizes = [7]
    median_ksizes = [5]
    morph_ksizes_x = [2]
    morph_ksizes_y = [2]

    def func(frame, monitor, gui_x, **kwargs):
        cvui.text(where=monitor, x=gui_x+20, y=10,  text="[Pencil Sketch]")
        idx = cvui.radiobox(where=monitor, x=gui_x, y=30, labels=labels, states=states)
        cvui.text(where=monitor, x=gui_x,    y=170,  text="Median Blur ksize")
        median_ksize = cvui.trackbar(where=monitor, x=gui_x, y=190, width=140, value=median_ksizes, min=1, max=15,  labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=2)
        cvui.text(where=monitor, x=gui_x,    y=250,  text="Laplacian ksize")
        lap_ksize = cvui.trackbar(where=monitor, x=gui_x, y=270, width=140, value=lap_ksizes,      min=1, max=15,  labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=2)
        cvui.text(where=monitor, x=gui_x, y=330,  text="Binarization method")
        bi_idx = cvui.radiobox(where=monitor, x=gui_x, y=350, labels=bi_labels, states=bi_states)
        cvui.text(where=monitor, x=gui_x, y=420,  text="Binarization threshold")
        bi_thresh  = cvui.trackbar(where=monitor, x=gui_x, y=440, width=140, value=bi_thresholds,   min=0, max=255, labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=1)
        cvui.text(where=monitor, x=gui_x, y=500,  text="Binarization block size")
        bi_blockSize = cvui.trackbar(where=monitor, x=gui_x, y=520, width=140, value=bi_blockSizes,   min=3, max=25, labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=2)
        cvui.text(where=monitor, x=gui_x, y=580,  text="Binarization constant value.")
        bi_const = cvui.trackbar(where=monitor, x=gui_x, y=600, width=140, value=bi_consts,   min=1, max=15, labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=1)
        cvui.text(where=monitor, x=gui_x, y=660, text="Morphological ksize")
        cvui.text(where=monitor, x=gui_x, y=690,  text="x")
        morph_ksize_x = cvui.trackbar(where=monitor, x=gui_x+5,  y=680, width=70, value=morph_ksizes_x,  min=1, max=10,  labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=1)
        cvui.text(where=monitor, x=gui_x+80, y=690,  text="y")
        morph_ksize_y = cvui.trackbar(where=monitor, x=gui_x+85, y=680, width=70, value=morph_ksizes_y,  min=1, max=10,  labelfmt="%.1Lf", options=cvui.TRACKBAR_DISCRETE, discreteStep=1)        

        if idx>=1:
            # 1. Convert to Gray Scale.
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        if idx>=2:
            # 2. Blur
            frame = cv2.medianBlur(src=frame, ksize=median_ksize)
        if idx>=3:
            # 3. Laplacian
            frame = cv2.Laplacian(src=frame, ddepth=cv2.CV_8U, ksize=lap_ksize)
        if idx>=4:
            # 4. Binarization.
            frame = binarizer_creator(method=bi_labels[bi_idx], thresh=bi_thresh, blockSize=bi_blockSize, const=bi_const)(src=frame)
        if idx>=5:
            # 5. Morphological Transformations.
            kernel = np.ones(shape=(morph_ksize_y, morph_ksize_x), dtype=np.uint8)
            frame = cv2.dilate(src=frame, kernel=kernel, iterations=1)
            frame = cv2.erode(src=frame, kernel=kernel, iterations=1)
        return frame

    project.wrap(func=func)