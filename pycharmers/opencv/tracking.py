#coding: utf-8
import os
import cv2

from ._path import save_dir_create
from .video_image_handler import basenaming
from .drawing import SUPPORTED_COORD_TYPES, draw_bboxes_create, draw_text_with_bg
from .windows import cvKeys, FrameWindow, DEFAULT_FRAME_KEYS
from ..utils.generic_utils import get_create, handleKeyError
from ..utils.json_utils import save_json
from ..utils._colorings import toBLUE, toGREEN


DEFAULT_TRACKING_KEYS = DEFAULT_FRAME_KEYS.copy()
DEFAULT_TRACKING_KEYS.update({
    "TRACKING" : {"start": "t", "stop": "c", "init": "n"},
})
all = PYCHARMERS_TRACKER_CREATORS = {
    "boosting"   : cv2.TrackerBoosting_create,
    "csrt"       : cv2.TrackerCSRT_create,
    "goturn"     : cv2.TrackerGOTURN_create,
    "kcf"        : cv2.TrackerKCF_create,
    "mil"        : cv2.TrackerMIL_create,
    "mosse"      : cv2.TrackerMOSSE_create,
    "medianflow" : cv2.TrackerMedianFlow_create,
    "tld"        : cv2.TrackerTLD_create,
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

class TrackingWindow(FrameWindow):
    """OpenCV window for Trackings (images or video).

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import TrackingWindow, SAMPLE_VTEST_VIDEO
        >>> window = TrackingWindow(path=SAMPLE_VTEST_VIDEO, tracker="boosting", coord_type="xywh")
        >>> # window.describe()
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    def __init__(self, path, tracker="boosting", coord_type="xywh", bbox=(0,0,0,0),
                 winname=None, dirname=None, move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_TRACKING_KEYS), **metadata):
        super().__init__(
            path,
            winname=winname,
            dirname=dirname,
            move_distance=move_distance,
            expansion_rate=expansion_rate,
            cvKey=cvKey,
        )
        self.moveWindow(0, 0)
        # Preparation for Tracking
        self.draw_bboxes = draw_bboxes_create(coord_type=coord_type)
        self.tracker = tracker_create(tracker)
        self.logger = None
        self.bbox = self.init(bbox=bbox, coord_type=coord_type, input_path=path, dirname=dirname, tracking_method=str(tracker)) 

    def init(self, bbox=(0,0,0,0), coord_type="xywh", input_path=None, dirname=None, **metadata):
        if self.logger is not None: 
            self.logger.save()
        self.logger = BBoxLogger(coord_type=coord_type, input_path=input_path, dirname=dirname, **metadata)

        # Get curt (initial) frame.
        frame = self.gen.__next__()
        self.gen = self.frame_generator(*self.input_path, frame_num=self.frame_num)
        winname = self.winname + "_initial_bbox"
        if min((bbox[-2:])) == 0:
            bbox = cv2.selectROI(windowName=winname, img=frame, showCrosshair=True, fromCenter=False)
        else:
            frame = self.draw_bboxes(frame=frame, bboxes=bbox, info={"text": "initial"})  
            cv2.imshow(winname, frame)
        self.tracker.init(frame, bbox) 
        self.logger.add_bboxes(no=self.frame_num, bboxes=bbox)
        return bbox

    def recieveKey(self, key):
        """Response according to Recieved key.

        Args:
            key (int): Input Key. (= ``cv2.waitKey(0)``)

        Returns:
            is_break (bool) Whether loop break or not. If break, destroy the window.
        """
        is_break = False
        cvKey = self.cvKey
        
        if key in cvKey.TRACKING_KEYS_ORD:
            if key==cvKey.TRACKING_KEYS_ORD:
                for frame in self.gen:
                    track, bbox = self.tracker.update(frame)
                    self.logger.add_bboxes(no=self.frame_num, bbox=bbox)
                    if track:
                        bbox = [int(e) for e in bbox]
                        frame = self.draw_bboxes(frame=frame, bboxes=bbox)
                    else:
                        draw_text_with_bg(
                            img=frame, text="failure", org=(50,50),
                            fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=3,
                            color="red", bgcolor="white", color_type="css4",
                            thickness=1,
                        )
                    self.show(frame)
                    k = cv2.waitKey(1)
                    if k==cvKey.TRACKING_STOP_KEY_ORD: break
            elif key==cvKey.TRACKING_INIT_KEY_ORD:
                self.bbox = self.init_bbox(bbox=(0,0,0,0))   
        else:
            is_break = super().recieveKey(key)
        return is_break


    def _ret_info(self):
        """ Return Key Information. """
        cvKey = self.cvKey
        info  = super()._ret_info()
        info += f"""\
        # Tracking
        - To {toGREEN('start')+' tracking,':<25} press '{toBLUE(cvKey.TRACKING_START_KEY_STR)}'
        - To {toGREEN('stop')+' tracking,':<25} press '{toBLUE(cvKey.TRACKING_STOP_KEY_STR)}'
        - To {toGREEN('initialize')+' bbox,':<25} press '{toBLUE(cvKey.TRACKING_INIT_KEY_STR)}'
        """
        return info