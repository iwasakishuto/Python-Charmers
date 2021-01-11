#coding: utf-8
import cv2
import numpy as np

def findBiggestContour(contours, eta=0.1):
    """
    Args:
        contours (list) : Contours. (e.g. The return of ``cv2.findContours`` )

    Returns:
        biggest (np.ndarray) : Countour of the biggest area.
        max_area (int)       : Area of the biggest area.

    Examples:
        >>> from pycharmers.opencv import findBiggestContour, SAMPLE_LENA_IMG
        >>> img_gray = cv2.imread(SAMPLE_LENA_IMG, 0)
        >>> img_th = cv2.Canny(img_gray, 100, 100)
        >>> contours, hierarchy = cv2.findContours(image=img_th, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
        >>> biggest, max_area = findBiggestContour(contours, eta=0.2)
        >>> max_area
        0 # There is no closed countour.
    """
    biggest = np.array([])
    max_area = 0
    for contour in contours:
        area = cv2.contourArea(contour)
        epsilon = eta * cv2.arcLength(curve=contour, closed=True)
        approx = cv2.approxPolyDP(curve=contour, epsilon=epsilon, closed=True)
        if area > max_area and len(approx) == 4:
            biggest = approx
            max_area = area
    return biggest, max_area

def reorder_contour(points):
    """Reorder the points created by ``cv2.approxPolyDP``

    Args:
        points (np.ndarray) : Points.

    Returns:
        ret (np.ndarray) : Reordered Points.
    """
    points  = points.reshape((4, 2))
    ret = np.zeros((4, 1, 2), dtype=np.int32)
    sum  = np.sum(points, axis=1)
    diff = np.diff(points, axis=1)

    ret[0] = points[np.argmin(sum)]
    ret[1] = points[np.argmin(diff)]
    ret[2] = points[np.argmax(diff)]
    ret[3] = points[np.argmax(sum)]
    return ret