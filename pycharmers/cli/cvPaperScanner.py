#coding: utf-8
import sys
import cv2
import numpy as np
from ..utils import cv2ArgumentParser
from ..opencv import cvui, cv2Project
from ..opencv import draw_text_with_bg, findBiggestContour, reorder_contour, draw_bboxes_xywh

def cvPaperScanner(argv=sys.argv[1:]):
    """Paper Scanner using OpenCV.

    Please see :meth:`cv2ArgumentParser <pycharmers.utils.argparse_utils.cv2ArgumentParser>` for arguments.

    Note:
        When you run from the command line, execute as follows::

        $ cv-paper-scanner --cam 0 --radio-width 200

    +--------------------------------------------+
    |                Sample                      |
    +============================================+
    | .. image:: _images/cli.cvPaperScanner.gif  |
    +--------------------------------------------+
    """
    parser = cv2ArgumentParser(prog="cv-paper-scan", description="Paper Scanner", add_help=True)
    args = parser.parse_args(argv)
    project = cv2Project(args=args)

    labels      = ["Original", "Gray", "Canny Edge", "Contours", "Biggest Contour", "Warp Prespective", "Warp Gray", "Adaptive Threshold"]
    states      = [i==0 for i in range(len(labels))]
    threshold1  = [100]
    threshold2  = [200]
    eta_counter = [0.1]

    def func(frame, monitor, frame_width, frame_height, gui_x, **kwargs):
        cvui.text(where=monitor, x=gui_x+20,           y=30,  text="[Document Scanner]")
        idx = cvui.radiobox(where=monitor, x=gui_x,    y=60,  labels=labels, states=states)
        cvui.text(where=monitor, x=gui_x+20,           y=245, text="[Canny Edge]")
        cvui.text(where=monitor, x=gui_x,              y=270, text="* Low threshold")
        cvui.text(where=monitor, x=gui_x,              y=345, text="* High threshold")
        cvui.text(where=monitor, x=gui_x+20,           y=450, text="[Biggest Counter]")
        cvui.text(where=monitor, x=gui_x,              y=475, text="* eta")
        th1 = cvui.trackbar(where=monitor, x=gui_x,    y=290, width=150, value=threshold1, min=0., max=255.)
        th2 = cvui.trackbar(where=monitor, x=gui_x,    y=380, width=150, value=threshold2, min=0., max=255.)
        eta = cvui.counter(where=monitor,  x=gui_x+30, y=500, value=eta_counter, step=0.01, fmt="%.2f")
        img_bgr = frame.copy()
        # Gray
        if idx>=1:
            # Convert image to Gray scale.
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        # Canny Edge
        if idx>=2:
            # Add Gaussian Blur.
            img_blur = cv2.GaussianBlur(src=frame, ksize=(5, 5), sigmaX=1)
            # APPLY Canny Blur.
            img_th = cv2.Canny(image=img_blur, threshold1=th1, threshold2=th2)
            # Apply Dilation & Erosion.
            kernel = np.ones(shape=(5, 5), dtype=np.uint8)
            frame = cv2.erode(src=cv2.dilate(src=img_th, kernel=kernel, iterations=2), kernel=kernel, iterations=1) 
        # Contours"
        if idx>=3:
            # Find All Contours.
            contours, hierarchy = cv2.findContours(image=frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
            img_binary = frame.copy()
            frame = cv2.drawContours(image=frame, contours=contours, contourIdx=-1, color=(0, 255, 0), thickness=10)
        # Biggest Contour
        if idx>=4:
            # Find the biggest Contour
            biggest_contour, max_area = findBiggestContour(contours=contours, eta=eta)
            if max_area == 0:
                draw_text_with_bg(img=frame, text="Could not find the closed contours.", org=(10,50))
                idx = 4
            else:
                # Draw the biggest contour
                frame = img_binary
                biggest_contour = reorder_contour(biggest_contour)
                frame = cv2.drawContours(image=frame, contours=biggest_contour, contourIdx=-1, color=(0, 255, 0), thickness=20)
        # Warp Prespective
        if idx>=5:
            matrix = cv2.getPerspectiveTransform(src=np.float32(biggest_contour), dst=np.float32([[0, 0],[frame_width, 0], [0, frame_height],[frame_width, frame_height]]))
            frame = cv2.warpPerspective(src=img_bgr, M=matrix, dsize=(frame_width, frame_height))
        # Warp Gray
        if idx>=6:
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        # Adaptive Threshold
        if idx>=7:
            frame = cv2.adaptiveThreshold(src=frame, maxValue=255, adaptiveMethod=1, thresholdType=1, blockSize=7, C=2)
            frame = cv2.bitwise_not(src=frame)
            frame = cv2.medianBlur(src=frame, ksize=3)
        return frame
        
    project.wrap(func=func)