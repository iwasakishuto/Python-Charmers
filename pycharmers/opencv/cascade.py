#coding: utf-8
import os
import re
import pathlib
import cv2

from . import BASE_PATH

HAARCASCADES_PATH = os.path.join(BASE_PATH, "data", "haarcascades")
CASCADES_DICT = {
    re.sub(r"haarcascade_(.*)\.xml", r"\1", p.name) : os.path.join(HAARCASCADES_PATH, p.name) \
    for p in sorted(pathlib.Path(HAARCASCADES_PATH).glob("*.xml"))
}

def print_all_cascades():
    for name, path in CASCADES_DICT.items():
        print(f"- {name}: {os.path.basename(path)}")

def cascade_creator(name):
    if name not in CASCADES_DICT:
        raise KeyError(f"please choose from {', '.join(CASCADES_DICT.keys())}")
    return cv2.CascadeClassifier(CASCADES_DICT.get(name))

def cascade_detector(name):
    cascade = cascade_creator(name)
    def func(img, *args, expand_ratio=0.0):
        """
        @params img          : (ndarray) BGR Image. (= cv2.imread(path))
        @params *args        : parameter for `detectMultiScale`
        @params expand_ratio : (float) Edges will be expaned to
                               ( (1+2*expand_ratio)*w, (1+2*expand_ratio)*h )
        """
        H,W,_ = img.shape
        locations = []
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        results = cascade.detectMultiScale(gray, *args)
        for x,y,w,h in results:
            edge_w,edge_h = int(w*expand_ratio),int(h*expand_ratio)
            top    = max(y-edge_h,   0)
            bottom = min(y+h+edge_h, H)
            left   = max(x-edge_w,   0)
            right  = min(x+w+edge_w, W)
            locations.append((left,top,right,bottom))
        return locations
    return func