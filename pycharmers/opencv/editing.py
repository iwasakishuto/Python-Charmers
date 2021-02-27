# coding: utf-8
import os
import cv2
import warnings
import numpy as np

from .drawing import cv2WHITE
from ..utils.generic_utils import filenaming
from ..utils._colorings import toBLUE

def cv2paste(bg_img, fg_img, points=(0,0), inplace=False):
    """Pastes ``fg_image`` into ``bg_image``
    
    Args:
        bg_img (ndarray) : Background Image. shape=(H,W,ch)
        fg_img (ndarray) : Background Image. shape=(H,W,ch)
        points (tuple)   : Coordinates to paste. (x,y)
        inplace (bool)   : Whether to transform input ( ``bg_img`` ) using no auxiliary data structure.
        
    Returns:
        bg_img (ndarray) : pasted image.
        
    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG, cv2read_mpl, cv2plot, cv2paste
        >>> bg_img = cv2read_mpl(SAMPLE_LENA_IMG)
        >>> fg_img = cv2.resize(bg_img, dsize=(256,256))
        >>> ax = cv2plot(cv2paste(bg_img, fg_img, points=(128,128)))
    """
    if not inplace:
        bg_img = bg_img.copy()
        
    x,y = points
    bg_h, bg_w, _ = bg_img.shape
    fg_h, fg_w, _ = fg_img.shape
    
    if ((-fg_w < x < bg_w) and (-fg_h < y < bg_h)):
        if not inplace:
            bg_img = bg_img.copy()            
            bg_img[max(0,y):min(y+fg_h, bg_h), max(0,x):min(x+fg_w, bg_w), :] = fg_img[max(0,0-y):bg_h-y, max(0,0-x):bg_w-x, :]
    return bg_img

def vconcat_resize_min(*images, interpolation=cv2.INTER_CUBIC):
    """Concat vertically while resizing to the smallest width.

    Args:
        images (np.ndarray) : OpenCV images
        interpolation (int) : interpolation method, see `OpenCV Documentations #InterpolationFlags <https://docs.opencv.org/master/da/d54/group__imgproc__transform.html#ga5bb5a1fea74ea38e1a5445ca803ff121>`_
    
    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import vconcat_resize_min, cv2plot
        >>> images = [cv2.imread(path) for path in os.listdir("images")]
        >>> vconcat_img = vconcat_resize_min(*images)
        >>> ax = cv2plot(vconcat_img)
    """
    w_min = min(img.shape[1] for img in images)
    return cv2.vconcat([
        cv2.resize(src=img,
                   dsize=(w_min, int(img.shape[0]*w_min/img.shape[1])),
                   interpolation=interpolation
        ) for img in images
    ])

def hconcat_resize_min(*images, interpolation=cv2.INTER_CUBIC):
    """Concat horizontally while resizing to the smallest height.

    Args:
        images (np.ndarray) : OpenCV images
        interpolation (int) : interpolation method, see `OpenCV Documentations #InterpolationFlags <https://docs.opencv.org/master/da/d54/group__imgproc__transform.html#ga5bb5a1fea74ea38e1a5445ca803ff121>`_
    
    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import hconcat_resize_min, cv2plot
        >>> images = [cv2.imread(path) for path in os.listdir("images")]
        >>> hconcat_img = hconcat_resize_min(*images)
        >>> ax = cv2plot(hconcat_img)
    """
    h_min = min(img.shape[0] for img in images)
    return cv2.hconcat([
        cv2.resize(src=img,
                   dsize=(int(img.shape[1]*h_min/img.shape[0]), h_min),
                   interpolation=interpolation
        ) for img in images
    ])

def resize_aspect(src, dsize, interpolation=cv2.INTER_AREA):
    """Resize the image while keeping the aspect ratio.
    
    Args:
        src (np.ndarray)    : Input image.
        dsize (tuple)       : Output image size ( ``width`` , ``height``)
        interpolation (int) : Interpolation method (default= ``cv2.INTER_AREA`` )
        
    Returns:
        resized (np.ndarray) : Resized image.
        
    Examples:
        >>> import numpy as np
        >>> from pycharmers.opencv import resize_aspect
        >>> img = np.random.randint(low=0, high=255, size=(1080, 720, 3), dtype=np.uint8)
        >>> resized = resize_aspect(src=img, dsize=(300, 300))
        >>> resized.shape
        (300, 200, 3)
    """
    sh, sw = src.shape[:2]
    dw, dh = dsize
    
    if sh/sw > dh/dw:
        ratio = dh/sh
    else:
        ratio = dw/sw
    dsize = (int(ratio*sw), int(ratio*sh))
    resized = cv2.resize(src=src, dsize=dsize, interpolation=interpolation)
    return resized

def transparency(in_path, out_path=None, lower_bgr=cv2WHITE, upper_bgr=cv2WHITE, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE, thresh=None, check_exist=True):
    """Transparency processing.

    Args:
        in_path (str)         : Path to input image.
        out_path (str)        : Path to output image.
        lower_bgr (tuple/int) : Lower bound of image value to be transparent.
        upper_bgr (tuple/int) : Upper bound of image value to be transparent.
        mode (int)            : Contour retrieval mode used in ``cv2.findContours`` (default = ``cv2.RETR_EXTERNAL`` )
        method (int)          : ontour approximation method used in ``cv2.findContours`` (default = ``cv2.CHAIN_APPROX_SIMPLE`` )
        thresh (int)          : Threshold value.
        check_exist (bool)    : If ``True``, there is a possibility of overwriting the image.

    Examples:
        >>> from pycharmers.opencv import transparency, SAMPLE_LENA_IMG
        >>> transparency(SAMPLE_LENA_IMG)
        Saved at /Users/iwasakishuto/.pycharmers/opencv/image/lena_transparency.png
    """
    # Naming the output path.
    if out_path is None:
        root = os.path.splitext(in_path)[0] + "_transparency"
        ext = ".png"
    else:
        root,ext = os.path.splitext(out_path)
        if ext==".jpg":
            warnings.warn("Since transparent image cannot be created with '.jpg' image, use '.png'.")
            ext = ".png"
    out_path = root + ext
    if check_exist:
        out_path = filenaming(out_path)

    src = cv2.imread(filename=in_path, flags=cv2.IMREAD_UNCHANGED)
    if src.shape[2]==3:
        src = np.insert(src, 3, values=[0], axis=2)
    
    if thresh is None:
        # Checks if array elements lie between the elements of two other arrays.
        binary = 255-cv2.inRange(src=src[:,:,:3], lowerb=np.asarray(lower_bgr), upperb=np.asarray(upper_bgr))
    else:
        # Thresholding
        gray = cv2.imread(filename=in_path, flags=cv2.IMREAD_GRAYSCALE)
        binary = cv2.threshold(gray, thresh=thresh, maxval=255, type=cv2.THRESH_BINARY)[1]
    contours, _ = cv2.findContours(image=binary, mode=mode, method=method)
    mask = np.zeros_like(binary, dtype=np.uint8)
    src[:,:,3] = cv2.fillPoly(img=mask, pts=contours, color=255)
    if cv2.imwrite(filename=out_path, img=src):
        print(f"Saved at {toBLUE(out_path)}")

def pil2cv(img):
    """Convert ``PIL.Image`` object into ``numpy`` array. (BGR)"""
    return cv2.cvtColor(np.asarray(img, dtype=np.uint8), cv2.COLOR_RGBA2BGR)