#coding: utf-8
import re
import sys
import argparse
import cv2
import numpy as np
from pycharmers.__meta__ import __version__
from pycharmers.opencv import cvui, cascade_creator, draw_bboxes_xywh
from pycharmers.opencv.cascade import OPENCV_CASCADES

def cvCascades(argv=sys.argv[1:]):
    """Control the OpenCV cascade Examples.

    Args:
        --winname (str)     : Window name.
        --cam (int)         : The ID of the web camera.
        --radio-width (int) : The width of the radio boxes.

    Note:
        When you run from the command line, execute as follows::

        $ cv-Cascades --cam 0 --radio-width 200
    """
    parser = argparse.ArgumentParser(prog="cv-Cascades", description="OpenCV cascade Examples", add_help=True)
    parser.add_argument("--winname",     type=str, default=f"Cascade Example (Pycharmers {__version__})", help="Window name.")
    parser.add_argument("--path",        type=str, help="Path to video.")
    parser.add_argument("--cam",         type=int, default=0,   help="Define the id of the web camera. `cv2.VideoCapture( [ID] )`")
    parser.add_argument("--radio-width", type=int, default=200, help="The width of the radio boxes.")
    args = parser.parse_args(argv)

    winname = args.winname
    path = args.path
    radio_width = args.radio_width

    if path is None:
        cap = cv2.VideoCapture(args.cam)
    else:
        cap = cv2.VideoCapture(path)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    bg_frame = np.zeros(shape=(height, width+radio_width, 3), dtype=np.uint8)

    # Collect All cascades.
    cascade_names, cascades, states = [],[],[]
    for name,value in OPENCV_CASCADES.items():
        m = re.match(pattern=r"^haarcascades:haarcascade_(.+)$", string=name)
        if m is not None:
            try:
                cascade = cascade_creator(cascade=name)
                cascades.append(cascade)
                states.append(len(states)==0)
                cascade_names.append(m.group(1))
            except Exception as e:
                print(name, e)

    cvui.init(winname)
    cv2.moveWindow(winname=winname, x=0, y=0)
    while (True):
        bg_frame[:] = (49, 52, 49)
        ret, frame = cap.read()

        if (not ret) or cvui.button(where=bg_frame, x=width+10, y=10, label="&Quit"): 
            break
        idx = cvui.radiobox(where=bg_frame, x=width+10, y=50, labels=cascade_names, states=states)

        cascade, name = cascades[idx], cascade_names[idx]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for bbox in cascade.detectMultiScale(gray):
            draw_bboxes_xywh(frame=frame, bboxes=bbox, infos=[{"color":(56, 47, 114), "text": name}])
        bg_frame[:height, :width, :] = frame

        cvui.update()
        cv2.imshow(winname, bg_frame)
        if cv2.waitKey(1) == cvui.ESCAPE:
            break
    cv2.destroyAllWindows()
    cap.release()