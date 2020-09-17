# coding: utf-8
import cv2

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