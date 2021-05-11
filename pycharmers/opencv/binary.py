#coding: utf-8
import cv2
import numpy as np
from ..utils.generic_utils import handleKeyError, handleTypeError

OPENCV_BINARYZATIONS = {
    "fixed"    : None,
    "mean"     : cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    "gaussian" : cv2.ADAPTIVE_THRESH_MEAN_C,
}

def binarizer_creator(method, maxval=255, thresh=127, thresholdType=cv2.THRESH_BINARY, blockSize=11, const=2):
    """Returns a function which performs advanced morphological transformations.

    Args:
        method (str/int)    : The identifier of binarization.
        thresh (int)        : Threshold value used in ``"fixed"`` binarizer.
        maxval (int)        : The maximum value.
        thresholdType (int) : Thresholding type.
        blockSize (odd)     : Size of a pixel neighborhood that is used to calculate a threshold value for the pixel: ``3`` , ``5`` , ``7`` , and so on.
        const (int)         : Constant subtracted from the mean or weighted mean (see the details below). Normally, it is positive but may be zero or negative as well.

    Returns:
        function : Binarizer.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import binarizer_creator, SAMPLE_LENA_IMG, vconcat_resize_min, cv2plot
        >>> from pycharmers.opencv.binary import OPENCV_BINARYZATIONS
        >>> gray = cv2.imread(SAMPLE_LENA_IMG, 0)
        >>> images = [gray]
        >>> images.extend([binarizer_creator(key)(gray) for key in OPENCV_BINARYZATIONS.keys()])
        >>> ax = cv2plot(vconcat_resize_min(*images), cmap="binary", figkeywargs={"figsize": (10,10)})
    """
    handleTypeError(types=[str, int], method=method)
    handleKeyError(lst=list(OPENCV_BINARYZATIONS.keys()), method=method)
    if method == "fixed":
        binarizer = lambda src, thresh=thresh, type=thresholdType : cv2.threshold(src=src, thresh=thresh, maxval=maxval, type=type)[1]
    else:
        adaptiveMethod = OPENCV_BINARYZATIONS.get(method, method)
        binarizer = lambda src, blockSize=blockSize, C=const : cv2.adaptiveThreshold(src=src, maxValue=maxval, adaptiveMethod=adaptiveMethod, thresholdType=thresholdType, blockSize=blockSize, C=C)
    return binarizer

def findBiggestContour(contours, eta=0.1):
    """
    Args:
        contours (list) : Contours. (e.g. The return of ``cv2.findContours`` )

    Returns:
        biggest (np.ndarray) : Countour of the biggest area.
        max_area (int)       : Area of the biggest area.

    Examples:
        >>> import cv2
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