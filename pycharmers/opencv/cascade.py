#coding: utf-8
import os
import cv2
import glob

from ..utils.generic_utils import handleKeyError, handleTypeError
from ._cvpath import PYCHARMERS_OPENCV_DATA_DIR

OPENCV_CASCADES = {
    os.path.splitext(":".join(path.split("/")[-2:]))[0] : path
    for path in glob.glob(f"{PYCHARMERS_OPENCV_DATA_DIR}/**/*cascade*.xml")
}

def cascade_creator(cascade):
    """Create a ``cv2.CascadeClassifier`` instance.
    Args:
        cascade (str, cv2.CascadeClassifier) : The identifier of Cascades.

    Returns:
        ``cv2.CascadeClassifier``

    Examples:
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG, cv2read_mpl, cv2plot, cascade_creator, draw_bboxes_xywh
        >>> cascade = cascade_creator(cascade="haarcascades:haarcascade_frontalface_alt2")
        >>> gray = cv2read_mpl(SAMPLE_LENA_IMG, 0)
        >>> for bbox in cascade.detectMultiScale(gray):
        ...     draw_bboxes_xywh(
        ...         frame=gray, bboxes=bbox
        ...     )
        >>> ax = cv2plot(gray)
    """
    handleTypeError(types=[cv2.CascadeClassifier, str], cascade=cascade)
    if isinstance(cascade, str):
        handleKeyError(lst=list(OPENCV_CASCADES.keys()), cascade=cascade)
        cascade = cv2.CascadeClassifier(OPENCV_CASCADES.get(cascade))
    return cascade

def cascade_detection_create(cascade):
    """Create a ``cascade_detection`` function.

    Args:
        cascade (str, cv2.CascadeClassifier) : Identifier for ``cv2.CascadeClassifier``

    Returns:
        ``cascade_detection``

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG, cv2read_mpl, cv2plot, cascade_detection_create, draw_bboxes_ltrb
        >>> cascade_detection = cascade_detection_create(cascade="haarcascades:haarcascade_frontalface_alt2")
        >>> img = cv2.cvtColor(cv2.imread(SAMPLE_LENA_IMG), cv2.COLOR_BGR2RGB) 
        >>> for bbox in cascade_detection(img):
        ...     draw_bboxes_ltrb(frame=img, bboxes=bbox)
        >>> ax = cv2plot(img)
    """
    cascade = cascade_creator(cascade)
    def cascade_detection(rgb, *args, expand_ratio=0.0):
        H,W,_ = rgb.shape
        locations = []
        gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
        results = cascade.detectMultiScale(gray, *args)
        for x,y,w,h in results:
            edge_w,edge_h = int(w*expand_ratio),int(h*expand_ratio)
            top    = max(y-edge_h,   0)
            bottom = min(y+h+edge_h, H)
            left   = max(x-edge_w,   0)
            right  = min(x+w+edge_w, W)
            locations.append((left,top,right,bottom))
        return locations
    cascade_detection.__doc__ = """Detect using the specified ``cv2.CascadeClassifier``.

    Args:
        rgb (np.ndarray)     : RGB Image. (= ``cv2read_mp()`` )
        expand_ratio (float) : Edges will be expaned to ``( (1+2*expand_ratio)*w, (1+2*expand_ratio)*h )``
    """
    return cascade_detection