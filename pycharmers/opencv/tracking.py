#coding: utf-8
import os
import cv2

from ._cvpath import save_dir_create
from .video_image_handler import basenaming
from .drawing import SUPPORTED_COORD_TYPES, draw_bboxes_create, draw_text_with_bg
from ..utils.generic_utils import get_create, handleKeyError
from ..utils.json_utils import save_json
from ..utils._colorings import toBLUE, toGREEN

all = OPENCV_TRACKER_CREATORS = {
    # "boosting"   : cv2.TrackerBoosting_create, # cv2.legacy_TrackerBoosting
    # "csrt"       : cv2.TrackerCSRT_create, # Comment out if you use opencv-python
    "goturn"     : cv2.TrackerGOTURN_create,
    # "kcf"        : cv2.TrackerKCF_create,  # Comment out if you use opencv-python
    "mil"        : cv2.TrackerMIL_create,
    # "mosse"      : cv2.TrackerMOSSE_create, # cv2.legacy_TrackerMOSSE
    # "medianflow" : cv2.TrackerMedianFlow_create,
    # "tld"        : cv2.TrackerTLD_create,
}

tracker_create = get_create(corresp_dict=all, class_=[cv2.Tracker], genre="tracker")
tracker_create.__doc__ += """
    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import tracker_create
        >>> boosting = tracker_create("boosting")
        >>> boosting
        <TrackerBoosting 0x122398c50>
        >>> boosting = tracker_create(cv2.TrackerBoosting_create())
        >>> boosting
        <TrackerBoosting 0x122398f50>
        >>> boosting = tracker_create(cv2.TrackerBoosting)
        TypeError: identifier must be one of ['cv2.Tracker', 'str'], not type
"""

class BBoxLogger():
    """Store Bounding Boxes logs.

    Args:
        input_path (str)      : Path to input image directory or video.
        coord_type (str)      : Coordinate types.

    Examples:
        >>> from pycharmers.utils import pycat
        >>> from pycharmers.opencv import BBoxLogger
        >>> bbox_logger = BBoxLogger()
        >>> bbox_logger.add_bboxes(no=1, bboxes=[(120,120,40,40)])
        >>> out_path = bbox_logger.save()
        tracking info was saved at /Users/iwasakishuto/.pycharmers/opencv/json/2020-09-25@01.05.18.json
        >>> pycat(out_path)
        {
        "coord_type": "xywh",
        "BBoxes": {
            "1": [
            [
                120,
                120,
                40,
                40
            ]
            ]
        }
        }
    """
    def __init__(self, coord_type="xywh", input_path=None, dirname=None, **metadata):
        handleKeyError(lst=SUPPORTED_COORD_TYPES, coord_type=coord_type)
        self.init(input_path=input_path, coord_type=coord_type, **metadata)
        # Bounding Box Convertor.
        self.dirname = dirname

    def init(self, input_path=None, coord_type="xywh", **metadata):
        """Initialization of the logs."""
        self.BBoxes = {}
        self.logs = {"coord_type" : coord_type}
        if input_path is not None:
            self.logs["abs_path"] = os.path.abspath(input_path)
            self.logs["is_video"] = os.path.isfile(input_path)
        self.logs.update(metadata)

    def add_bboxes(self, no, bboxes):
        """Add Bounding Boxes
        
        Args:
            no (int)      : Frame number.
            bboxes (list) : List of bounding boxes.
        """
        self.BBoxes[no] = bboxes

    def save(self, out_path=None):
        """Save the results"""
        out_path = out_path or save_dir_create(dirname=self.dirname, image=False, video=False, json=True)[0]
        self.logs["BBoxes"] = self.BBoxes
        save_json(obj=self.logs, file=out_path)
        print(f"tracking info was saved at {toBLUE(out_path)}")
        return out_path