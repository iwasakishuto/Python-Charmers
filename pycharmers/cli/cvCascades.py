#coding: utf-8
import re
import sys
import cv2
import numpy as np
from ..utils import cv2ArgumentParser
from ..opencv import cvui, cv2Project
from ..opencv import cascade_creator, draw_bboxes_xywh, cv2GREEN
from ..opencv.cascade import OPENCV_CASCADES

def cvCascades(argv=sys.argv[1:]):
    """Control the OpenCV cascade Examples.

    Please see :meth:`cv2ArgumentParser <pycharmers.utils.argparse_utils.cv2ArgumentParser>` for arguments.

    Note:
        When you run from the command line, execute as follows::

        $ cv-cascades --cam 0 --radio-width 200    
    """
    parser = cv2ArgumentParser(prog="cv-cascades", description="OpenCV cascade examples", add_help=True)
    args = parser.parse_args(argv)

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

    project = cv2Project(args=args, cascade_names=cascade_names)

    def func(frame, monitor, gui_x, frame_height, cascade_names, **kwargs):
        cvui.text(where=monitor,           x=gui_x+20, y=5,  text="[Cascade List]")
        idx = cvui.radiobox(where=monitor, x=gui_x,    y=25, labels=cascade_names, states=states)
        cascade = cascades[idx]
        name = cascade_names[idx]
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for bbox in cascade.detectMultiScale(gray):
            draw_bboxes_xywh(frame=frame, bboxes=bbox, infos=[{"color":cv2GREEN, "text": name}])
        return frame
        
    project.wrap(func=func)