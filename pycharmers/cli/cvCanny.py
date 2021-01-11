# coding: utf-8
import cv2
import sys
import argparse
import numpy as np
from pycharmers.opencv import cvui, SAMPLE_LENA_IMG

def cvCany(argv=sys.argv[1:]):
    """Control the application of the Canny edge algorithm to a loaded image.
    
    Args:
        path (str)   : Path to image.
        --name (str) : Window name.

    Note:
        When you run from the command line, execute as follows::
        
        $ cvCany path/to/sample.png    
    """
    parser = argparse.ArgumentParser(prog="pdfmine", add_help=True)
    parser.add_argument("path",   type=str, help="Path/to/input image.")
    parser.add_argument("--name", type=str, default="CVUI Canny Edge", help="Window name.")
    args = parser.parse_args(argv)

    window_name = args.name
    img = cv2.imread(args.path)
    frame = np.zeros_like(a=img, dtype=np.uint8)
    
    low_th, high_th, use_canny = [50], [150], [False]
    cvui.init(window_name)

    while (True):
        if use_canny[0]:
            frame = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            frame = cv2.Canny(frame, low_th[0], high_th[0], 3)
            frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2BGR)
        else: 
            frame[:] = img[:]

        cvui.window(frame, 10, 50, 180, 200, 'Settings')
        cvui.checkbox(frame, 15, 80, 'Use Canny Edge', use_canny)
        cvui.text(frame, 15, 110, 'Low threshold')
        cvui.trackbar(frame, 15, 130, 165, low_th,  5,  150)
        cvui.text(frame, 15, 180, 'High threshold')
        cvui.trackbar(frame, 15, 200, 165, high_th, 80, 300)
        cvui.update()
        cv2.imshow(window_name, frame)
        if cv2.waitKey(20) == cvui.ESCAPE:
            break