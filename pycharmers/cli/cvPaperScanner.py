#coding: utf-8
import re
import sys
import argparse
import cv2
import numpy as np
from pycharmers.__meta__ import __version__
from pycharmers.opencv import cvui, draw_bboxes_xywh, findBiggestContour, draw_text_with_bg, VideoCaptureCreate, reorder_contour

def cvPaperScanner(argv=sys.argv[1:]):
    """Control the OpenCV cascade Examples.

    Args:
        --winname (str)     : Window name.
        --path (str)        : Path to video or image.
        --cam (int)         : The ID of the web camera.
        --radio-width (int) : The width of the radio boxes.

    Note:
        When you run from the command line, execute as follows::

        $ cv-paper-scanner --cam 0 --radio-width 200
    """
    parser = argparse.ArgumentParser(prog="cv-PaperScan", description="Paper Scanner", add_help=True)
    parser.add_argument("--winname",     type=str, default=f"Paper Scanner (Pycharmers {__version__})", help="Window name.")
    parser.add_argument("--path",        type=str, help="Path to video or image.")
    parser.add_argument("--cam",         type=int, default=0,   help="Define the id of the web camera. `cv2.VideoCapture( [ID] )`")
    parser.add_argument("--radio-width", type=int, default=200, help="The width of the radio boxes.")
    args = parser.parse_args(argv)

    winname = args.winname
    radio_width = args.radio_width
    cap = VideoCaptureCreate(path=args.path, cam=args.cam)
    # cap.set(cv2.CAP_PROP_BRIGHTNESS, 160)
    width, height = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    bg_frame = np.zeros(shape=(height, width+radio_width, 3), dtype=np.uint8)

    labels = ["Original", "Gray", "Canny Edge", "Contours", "Biggest Contour", "Warp Prespective", "Warp Gray", "Adaptive Threshold"]
    states = [True if i==0 else False for i in range(len(labels))]
    threshold1 = [100]
    threshold2 = [200]
    eta_counter = [0.1]

    cvui.init(winname)
    cv2.moveWindow(winname=winname, x=0, y=0)
    while (True):
        bg_frame[:] = (49, 52, 49)
        ret, frame = cap.read()

        if (not ret) or cvui.button(where=bg_frame, x=width+10, y=10, label="&Quit"): 
            break
        idx = cvui.radiobox(where=bg_frame, x=width+10, y=50,  labels=labels, states=states)
        cvui.text(where=bg_frame, x=width+30, y=270, text="[Canny Edge]")
        cvui.text(where=bg_frame, x=width+10, y=290, text="Low threshold")
        cvui.text(where=bg_frame, x=width+10, y=360, text="High threshold")
        cvui.text(where=bg_frame, x=width+30, y=450, text="[Biggest Counter]")
        cvui.text(where=bg_frame, x=width+10, y=470, text="eta")
        th1 = cvui.trackbar(where=bg_frame, x=width+10, y=310, width=150, value=threshold1, min=0., max=255.)
        th2 = cvui.trackbar(where=bg_frame, x=width+10, y=380, width=150, value=threshold2, min=0., max=255.)
        eta = cvui.counter(where=bg_frame, x=width+10, y=500, value=eta_counter, step=0.01, fmt="%.2f")

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
            matrix = cv2.getPerspectiveTransform(src=np.float32(biggest_contour), dst=np.float32([[0, 0],[width, 0], [0, height],[width, height]]))
            frame = cv2.warpPerspective(src=img_bgr, M=matrix, dsize=(width, height))
        # Warp Gray
        if idx>=6:
            frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)
        # Adaptive Threshold
        if idx>=7:
            frame = cv2.adaptiveThreshold(src=frame, maxValue=255, adaptiveMethod=1, thresholdType=1, blockSize=7, C=2)
            frame = cv2.bitwise_not(src=frame)
            frame = cv2.medianBlur(src=frame, ksize=3)

        # draw_text_with_bg(img=frame, text=f"Method: {labels[idx]}", org=(height-50,50))
        cvui.beginRow(where=bg_frame, x=0, y=0)
        cvui.image(image=frame)
        cvui.endRow()
        cvui.update()
        cv2.imshow(winname, bg_frame)
        if cv2.waitKey(1) == cvui.ESCAPE:
            break
    cv2.destroyAllWindows()
    cap.release()