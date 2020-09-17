#coding: utf-8
import os
import re
import cv2
import numpy as np

from .editing import vconcat_resize_min, hconcat_resize_min
from ..utils.generic_utils import calc_rectangle_size

IMAGE_FILE_PATTERN = r".*\.(jpg|png|bmp|jpeg)"

def mono_frame_generator(path, frame_num=0):
    if os.path.isfile(path):
        video = cv2.VideoCapture(path)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            yield frame
        video.release()
    else:
        fn_list = sorted(os.listdir(path))[frame_num:]
        for fn in fn_list:
            frame = cv2.imread(os.path.join(path, fn))
            yield frame

def multi_frame_generator_sepa(*path, frame_num=0):
    """
    @return <zip> Generate multiple frames separately.
    """
    return zip(*[mono_frame_generator(p, frame_num=frame_num) for p in path])

def multi_frame_generator_concat(*paths, frame_num=0, grid=None):
    """
    @params grid : (nrow, ncol)
    """
    num_frames = len(paths)
    nrow, ncol = calc_rectangle_size(area=num_frames, w=None) if grid is None else grid
    expected_frames = nrow * ncol
    num_black_frame = expected_frames - num_frames

    names = [basenaming(path) for path in paths]
    max_name_len = 1
    for r in range(nrow):
        print(",".join(names[r*ncol:(r+1)*ncol]))

    gen = mono_frame_generator(paths[0])
    frame = gen.__next__()
    balck_frames = tuple(np.zeros_like(frame))*num_black_frame

    gens = multi_frame_generator_sepa(*paths, frame_num=frame_num)
    for frames in gens:
        frames += balck_frames
        concated_frame = vconcat_resize_min(*[
            hconcat_resize_min(*frames[r*ncol:(r+1)*ncol]) for r in range(nrow)
        ])
        yield concated_frame

def count_frame_num(path):
    if os.path.isfile(path):
        video = cv2.VideoCapture(path)
        frame_num = video.get(cv2.CAP_PROP_FRAME_COUNT)
    else:
        frame_num = sum([1 for fn in os.listdir(path) if re.search(IMAGE_FILE_PATTERN, fn, re.IGNORECASE)])
    return int(frame_num)

def basenaming(path):
    """ Base Naming
    @params path : path to video file, or directory which stores sequential images.
    @return name :
        if path is to video file (sample.mp4) -> sample
        if path is to directory (sample) -> sample
    """
    if os.path.isfile(path):
        # File. (Video)
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        # Directory. (stores sequential images.)
        name = os.path.basename(path)
    return name

def create_VideoWriter(in_path, method="", out_path=None, fps=30):
    """
    @params in_path  : (str) Input path.
    @params out_path : (str) Output path.
    """
    if out_path is None:
        exec_fn = os.path.splitext(os.path.basename(sys.argv[0]))[0]
        if len(method)>0 and method[0] != "-":
            method = "-" + method
        video_fn = f"{basenaming(in_path)}-{exec_fn}{method}.mp4"
        out_path = os.path.join(SAVE_PATH, video_fn)

    if os.path.isfile(in_path):
        video = cv2.VideoCapture(in_path)
        W = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
        H = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = video.get(cv2.CAP_PROP_FPS)
    else:
        for fn in os.listdir(in_path):
            img_path = os.path.join(in_path, fn)
            img = cv2.imread(img_path)
            if img is not None:
                break
        H,W,_ = img.shape
    out_video = cv2.VideoWriter(out_path, cv2.VideoWriter_fourcc('m','p','4','v'), int(fps), (W, H))
    return out_video