#coding: utf-8
import os
import re
import cv2
import warnings
import numpy as np

from .editing import vconcat_resize_min, hconcat_resize_min
from ..utils._colorings import toRED, toGREEN, toBLUE
from ..utils.generic_utils import calc_rectangle_size, now_str
from ..utils.print_utils import pretty_3quote
from ._cvpath import save_dir_create

from typing import Union,Optional,Tuple

IMAGE_FILE_PATTERN = r".*\.(jpg|png|bmp|jpeg)"

def mono_frame_generator(path, frame_no=0):
    """Mono frame Generator which displays a single frame in a video or single image in a directory.
    
    Args:
        path (str)      : ``path/to/images/directory`` or ``path/to/video.mp4``
        frame_no (int)  : If specified (``>0``), the image can be displayed from a specific positions.

    Returns:
        generator

    Examples:
        >>> from pycharmers.opencv import mono_frame_generator
        >>> from pycharmers.opencv import PYCHARMERS_OPENCV_IMAGE_DIR
        >>> for img in mono_frame_generator(path=PYCHARMERS_OPENCV_IMAGE_DIR):
        ...     print(img.shape)
        (512, 512, 3)
    """
    if os.path.isfile(path):
        video = cv2.VideoCapture(path)
        video.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
        while True:
            ret, frame = video.read()
            if not ret:
                break
            yield frame
        video.release()
    else:
        fn_list = sorted(os.listdir(path))[frame_no:]
        for fn in fn_list:
            frame = cv2.imread(os.path.join(path, fn))
            if frame is None:
                continue
            yield frame

def multi_frame_generator_sepa(*path, frame_no=0):
    """Multiple frame generator. (separatory)
    
    Args:
        path (str)     : ``path/to/images/directory`` or ``path/to/video.mp4``
        frame_no (int) : If specified (``>0``), the image can be displayed from a specific positions.

    Returns:
        generator

    Examples:
        >>> from pycharmers.opencv import multi_frame_generator_sepa
        >>> from pycharmers.opencv import PYCHARMERS_OPENCV_IMAGE_DIR
        >>> gen = multi_frame_generator_sepa(PYCHARMERS_OPENCV_IMAGE_DIR, PYCHARMERS_OPENCV_IMAGE_DIR)
        >>> for img in gen:
        ...     print(len(img), img[0].shape)
        2 (512, 512, 3)
    """
    return zip(*[mono_frame_generator(p, frame_no=frame_no) for p in path])

def multi_frame_generator_concat(*paths, frame_no=0, grid=None):
    """Multiple frame generator. (In a connected state)
        
    Args:
        path (str)      : ``path/to/images/directory`` or ``path/to/video.mp4``
        frame_no (int)  : If specified (``>0``), the image can be displayed from a specific positions.
        grid (tuple)    : How to concatenate the multiple frames. (ncols, nrows)

    Returns:
        generator

    Examples:
        >>> from pycharmers.opencv import multi_frame_generator_concat
        >>> from pycharmers.opencv import PYCHARMERS_OPENCV_IMAGE_DIR
        >>> gen = multi_frame_generator_concat(PYCHARMERS_OPENCV_IMAGE_DIR, PYCHARMERS_OPENCV_IMAGE_DIR, grid=(1,2))
        >>> for img in gen:
        ...     print(img.shape)
        (512, 1024, 3)
    """
    num_frames = len(paths)
    nrow, ncol = calc_rectangle_size(area=num_frames, w=None) if grid is None else grid
    expected_frames = nrow * ncol
    num_black_frame = expected_frames - num_frames

    names = [basenaming(path) for path in paths]
    max_name_len = 1

    gen = mono_frame_generator(paths[0])
    frame = gen.__next__()
    balck_frames = tuple(np.zeros_like(frame))*num_black_frame

    gens = multi_frame_generator_sepa(*paths, frame_no=frame_no)
    for frames in gens:
        frames += balck_frames
        concated_frame = vconcat_resize_min(*[
            hconcat_resize_min(*frames[r*ncol:(r+1)*ncol]) for r in range(nrow)
        ])
        yield concated_frame

def count_frame_num(path):
    """Count the number of frames.

    Args:
        path (str) : path to video file, or directory which stores sequential images.

    Examples:
        >>> from pycharmers.opencv import count_frame_num, SAMPLE_VTEST_VIDEO, PYCHARMERS_OPENCV_IMAGE_DIR
        >>> count_frame_num(SAMPLE_VTEST_VIDEO)
        795
        >>> count_frame_num(PYCHARMERS_OPENCV_IMAGE_DIR)
        1
    """
    if os.path.isfile(path):
        video = cv2.VideoCapture(path)
        frame_num = video.get(cv2.CAP_PROP_FRAME_COUNT)
    else:
        frame_num = len(list(filter(lambda fn: re.search(IMAGE_FILE_PATTERN, fn, re.IGNORECASE), os.listdir(path))))
    return int(frame_num)

def basenaming(path):
    """Returns the final component of a pathname.

    - If ``path`` indicates video file (``path/to/sample.mp4``) -> ``sample``
    - If ``path`` indicates directory (``path/to/sample``) -> ``sample``
  
    Args:
        path (str) : path to video file, or directory which stores sequential images.
    
    Examples:
        >>> import os
        >>> from pycharmers.opencv import basenaming
        >>> os.path.exists("path/to/sample.mp4")
        True
        >>> basenaming("path/to/sample.mp4")
        'sample'
        >>> basenaming("path/to/sample")
        'sample'
        >>> os.path.exists("path/to/sample2.mp4")
        False
        >>> basenaming("path/to/sample_.mp4")
        'sample_.mp4'
    """
    if os.path.isfile(path):
        # File. (Video)
        name = os.path.splitext(os.path.basename(path))[0]
    else:
        # Directory. (stores sequential images.)
        name = os.path.basename(path)
    return name

def VideoWriterCreate(input_path:Optional[str]=None, out_path:Optional[str]=None, codec:str="MP4V", fps:Optional[float]=None, size:Tuple[int,int]=(None,None), verbose:bool=False, **kwargs):
    """Create a ``cv2.VideoWriter`` which creates a video whose option is same as that of input.

    Args:
        input_path (Optional[str], optional) : Input media path for video/image file or image directory. Defaults to ``None``.
        out_path (Optional[str], optional)   : Output path for the created video. Defaults to ``None``.
        codec (str, optional)                : A video codec for the created output video.
        fps (float, optional)                : Frames Per Second. Defaults to ``None``.
        size (Tuple[int, int], optional)     : frame size for the created video. Defaults to ``(None, None)``.
        verbose (bool, optional)             : Whether to print the created ``cv2.VideoWriter`` info. Defaults to ``False``.

    Returns:
        cv2.VideoWriter : A instance of ``cv2.VideoWriter``.

    Examples:
        >>> from pycharmers.opencv import VideoWriterCreate
        >>> is_ok, VideoWriter = VideoWriterCreate(input_path=None, fps=30., height=360, width=480)
        (True, <VideoWriter 0x12597def0>)
        >>> is_ok, VideoWriter = VideoWriterCreate(input_path="path/to/video.mp4")
        (True, <VideoWriter 0x125345050>)
        >>> is_ok, VideoWriter = VideoWriterCreate(input_path="path/to/image_dir")
        (True, <VideoWriter 0x125345d70>)

    Raises:
        TypeError: When not enough information such as ``fps``, ``width``, or ``height``.
    """
    W, H = size
    if (input_path is None) or (not os.path.exists(input_path)):
        W = W or kwargs.get("width",  kwargs.get("W"))
        H = H or kwargs.get("height", kwargs.get("H"))
        if (W is None) or (H is None):
            raise TypeError(f"Please specify the {toGREEN('size')}(width,height) of the output video.")
    elif os.path.isfile(input_path):
        if re.search(pattern=IMAGE_FILE_PATTERN, string=input_path, flags=re.IGNORECASE):
            img = cv2.imread(input_path)
            H,W = img.shape[:2]
        else:
            video = cv2.VideoCapture(input_path)
            W = W or int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            H = H or int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = fps or video.get(cv2.CAP_PROP_FPS)
    else: # os.path.isdir(input_path):
        for fn in os.listdir(input_path):
            img_path = os.path.join(input_path, fn)
            img = cv2.imread(img_path)
            if img is not None:
                break
        W = W or img.shape[1]
        H = H or img.shape[0]
    if fps is None:
        raise TypeError(f"Please specify the {toGREEN('fps')} of the output video.")
    fourcc = cv2.VideoWriter_fourcc(*codec)
    ideal_ext = videocodec2ext(codec)
    if out_path is None:
        out_path = now_str() + ideal_ext
    else:
        root,original_ext = os.path.splitext(out_path)
        if original_ext != ideal_ext:
            warnings.warn(f"Change the file extension from {toRED(original_ext)} to {toGREEN(ideal_ext)} according to video codec ({toGREEN(codec)}).", category=RuntimeWarning)
            out_path = root + ideal_ext
    out_video = cv2.VideoWriter(out_path, fourcc, fps, (W,H))
    is_ok = out_video.isOpened()
    if not is_ok:
        warnings.warn(*pretty_3quote(toRED("""
        Could not make a typing video because VideoWriter was not created successfully. 
        Look at the warning text from OpenCV above and do what you need to do.
        """)))
        flag, status = (toRED("[failure]"), "can")
    else:
        flag, status = (toGREEN("[success]"), "can't")
    if verbose:
        print(*pretty_3quote(f"""
        {flag} {toGREEN("VideoWriter")} {status} be created.
        * Size (W,H)  : ({toGREEN(W)},{toGREEN(H)})
        * Video Codec : {toGREEN(codec)}
        * Output Path : {toBLUE(out_path)} 
        """))
    return (is_ok, out_video)

def VideoCaptureCreate(path=None, cam=0):
    """Create a VideoCapture (mimic) object.

    Args:
        path (str) : path to video or image.
        cam (int)  : The ID of the web camera

    Returns:
        cap (cv2.VideoCapture) : VideoCapture (mimic) object.

    Examples:
        >>> from pycharmers.opencv import VideoCaptureCreate, cv2plot
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG, SAMPLE_VTEST_VIDEO
        >>> for path in [SAMPLE_LENA_IMG, SAMPLE_VTEST_VIDEO, None]:
        ...     cap = VideoCaptureCreate(path=path, cam=0)
        ...     ret,frame = cap.read()
        ...     cv2plot(frame)
        ...     cap.release()
    """
    if path is None:
        cap = cv2.VideoCapture(cam)
    elif re.search(pattern=IMAGE_FILE_PATTERN, string=path, flags=re.IGNORECASE):
        class VideoMimic():
            def __init__(self, path):
                frame = cv2.imread(path)
                self.frame = frame
                self.info = {
                    cv2.CAP_PROP_FRAME_WIDTH  : frame.shape[1],
                    cv2.CAP_PROP_FRAME_HEIGHT : frame.shape[0],
                    cv2.CAP_PROP_FPS          : 30.0,
                }
            def read(self):
                return True, self.frame
            def release(self):
                return True
            def get(self, id):
                return self.info.get(id)  
            def set(self, id):
                pass
        cap = VideoMimic(path)
    else:
        cap = cv2.VideoCapture(path)
    return cap

def videocodec2ext(*codec) -> str:
    """Convert video codec to video extension.

    Args:
        codec (Union[tuple, str]) : Video Codec.    

    Returns:
        str: Ideal file extension.

    Examples:
        >>> from pycharmers.opencv import videocodec2ext
        >>> videocodec2ext("MP4V")
        '.mp4'
        >>> videocodec2ext("mp4v")
        '.mov'
        >>> videocodec2ext("VP80")
        '.webm'
        >>> videocodec2ext("XVID")
        '.avi
        >>> videocodec2ext("☺️")
        '.mp4'
    """
    if len(codec)==1 and isinstance(codec[0], str):
        codec = codec[0]
    else:
        codec = "".join(codec)
    return {
        "VP80": ".webm",
        "MP4S": ".mp4",
        "MP4V": ".mp4",
        "mp4v": ".mov",
        "H264": ".mp4",
        "X264": ".mp4",
        "DIV3": ".avi",
        "DIVX": ".avi",
        "IYUV": ".avi",
        "MJPG": ".avi",
        "XVID": ".avi",
        "THEO": ".ogg",
        "H263": ".wmv",
    }.get(codec, ".mp4")