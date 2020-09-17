#coding: utf-8
import os
import json
import pathlib
import cv2

from .video_image_utils import basenaming
from . import SAVE_PATH

TRACKER_CREATOR = {}
OPENCV_TRACKER_CREATOR = {
    "boosting"   : cv2.TrackerBoosting_create,
    "csrt"       : cv2.TrackerCSRT_create,
    "goturn"     : cv2.TrackerGOTURN_create,
    "kcf"        : cv2.TrackerKCF_create,
    "mil"        : cv2.TrackerMIL_create,
    "mosse"      : cv2.TrackerMOSSE_create,
    "medianflow" : cv2.TrackerMedianFlow_create,
    "tld"        : cv2.TrackerTLD_create,
}
TRACKER_CREATOR.update(OPENCV_TRACKER_CREATOR)
TRACKING_ALGORITHMS = list(TRACKER_CREATOR.keys())
COORDINATE_TYPES = ["xywh", "ltrb"]

def print_coord_info():
    message = \
    """
    [OpenCV]
    x,y,w,h = bbox
       (x,y) ------- (x+w,y)
         |              |
         |              |
         |              |
         |              |
      (x,y+h) ----- (x+w,y+h)
    [YOLO]
    l,t,r,b = bbox
       (l,t) -------- (r,t)
         |              |
         |              |
         |              |
         |              |
       (x,b) -------- (r,b)
    """
    print(message)


class TrackingLogger():
    def __init__(self, path, tracking_method, coord_type="xywh", **metadata):
        self.abs_path = str(pathlib.Path(path).resolve())
        self.is_video = os.path.isfile(path)
        self.tracking_method = tracking_method
        self.coord_type = coord_type
        self.save_info = {
            "xywh": ["x", "y", "width", "height"],
            "ltrb": ["left", "top", "right", "bottom"]
        }[coord_type] + list(metadata)
        self.ret_BBoxes = []

    def add_ret_bboxes(self, bboxes):
        """
        @params bboxes: Each bbox have only
            - left, top, right, bottom
        """
        # self.ret_BBoxes.append([
        #     dict(zip(self.save_info, bbox)) for bbox in bboxes
        # ])
        self.ret_BBoxes.append(bboxes)

    def save(self, out_path=None):
        # Handling the output path.
        if out_path is None:
            name = basenaming(self.abs_path)
            json_fn = f"{name}-{self.tracking_method}.json"
            out_path = os.path.join(SAVE_PATH, json_fn)

        results = {
            "abs_path": self.abs_path,
            "is_video": self.is_video,
            "coord_type": self.coord_type,
            "tracking_method": self.tracking_method,
            "save_info": self.save_info,
            "bounding_boxes": self.ret_BBoxes,
        }
        with open(out_path, mode="w") as f:
            json.dump(results, f)
        print(f"tracking info was saved at {out_path}.")