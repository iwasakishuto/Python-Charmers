# coding: utf-8
import cv2

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