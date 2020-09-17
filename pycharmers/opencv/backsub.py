#coding: utf-8
import cv2

BACKGROUND_SUBTRACTOR_CREATOR = {}
OPENCV_BACKGROUND_SUBTRACTOR_CREATOR = {
    "mog" : cv2.createBackgroundSubtractorMOG2,
    "knn" : cv2.createBackgroundSubtractorKNN,
}
BACKGROUND_SUBTRACTOR_CREATOR.update(OPENCV_BACKGROUND_SUBTRACTOR_CREATOR)
BACKGROUND_SUBTRACTION_ALGORITHMS = list(BACKGROUND_SUBTRACTOR_CREATOR.keys())