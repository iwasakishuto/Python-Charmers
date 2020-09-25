#coding: utf-8
import cv2

from ..utils.generic_utils import get_create

PYCHARMERS_BACKGROUND_SUBTRACTOR_CREATORS = {
    "mog" : cv2.createBackgroundSubtractorMOG2,
    "knn" : cv2.createBackgroundSubtractorKNN,
}
background_subtractor_create = get_create(corresp_dict=PYCHARMERS_BACKGROUND_SUBTRACTOR_CREATORS, class_=[cv2.BackgroundSubtractor], genre="background_subtractor")
background_subtractor_create.__doc__ += """
    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import background_subtractor_create
        >>> mog = background_subtractor_create("mog")
        >>> mog
        # <BackgroundSubtractorMOG2 0x12a165a30>
        >>> mog = background_subtractor_create(cv2.createBackgroundSubtractorMOG2())
        >>> mog
        # <BackgroundSubtractorMOG2 0x12a1658d0>
        >>> mog = background_subtractor_create(cv2.BackgroundSubtractorMOG2)
        TypeError: identifier must be one of ['cv2.BackgroundSubtractor', 'str'], not type
"""