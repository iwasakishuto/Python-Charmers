# coding: utf-8
import cv2

from ..utils.generic_utils import handleKeyError, handleTypeError

OPENCV_MORPHOLOGY_OPERATIONS = {
    "opening"  : cv2.MORPH_OPEN,
    "closing"  : cv2.MORPH_CLOSE,
    "gradient" : cv2.MORPH_GRADIENT,
    "tophat"   : cv2.MORPH_TOPHAT,
    "blackhat" : cv2.MORPH_BLACKHAT,
    "hitmiss"  : cv2.MORPH_HITMISS,
}
OPENCV_MORPHOLOGY_KERNEL_SHAPES = {
    "cross"  : cv2.MORPH_CROSS,
    "dilate" : cv2.MORPH_DILATE,
    "erode"  : cv2.MORPH_ERODE,
    "open"   : cv2.MORPH_OPEN,
}

def morph_kernel_creator(shape="erode", ksize=(5,5)):
    """Returns a structuring element of the specified size and shape for morphological operations.

    Args:
        shape (str, int) : Element shape.
        ksize (tuple)    : Size of the structuring element.

    Examples:
        >>> from pycharmers.opencv import morph_kernel_creator
        >>> kernel = morph_kernel_creator(shape="erode", ksize=(5,5))
        >>> kernel.shape
        (5, 5)
        >>> kernel = morph_kernel_creator(shape="erode", ksize=(3,5))
        >>> kernel.shape
        >>> (5, 3)
    """
    handleTypeError(types=[str, int], shape=shape)
    if isinstance(shape, str):
        handleKeyError(lst=list(OPENCV_MORPHOLOGY_KERNEL_SHAPES.keys()), shape=shape)
        shape = OPENCV_MORPHOLOGY_KERNEL_SHAPES.get(shape)
    return cv2.getStructuringElement(shape=shape, ksize=tuple(ksize))

def morph_transformer_creator(op, kernel=None, shape="erode", ksize=(5,5)):
    """Returns a function which performs advanced morphological transformations.

    Args:
        op (str, int)    : Type of a morphological operation
        kernel (array)   : Structuring element. It can be created using ``morph_kernel_creator``
                           The same can be achieved by giving values in the parameters (``shape``, ``ksize``).
        shape (str, int) : Element shape.
        ksize (tuple)    : Size of the structuring element.

    Examples:
        >>> from pycharmers.opencv import (SAMPLE_LENA_IMG, morph_transformer_creator,
                                        hconcat_resize_min, cv2plot, cv2read_mpl)
        >>> img = cv2read_mpl(SAMPLE_LENA_IMG, 0)
        >>> transformer = morph_transformer_creator(op="opening", shape="open", ksize=(12,12))
        >>> img_opening = transformer(img)
        >>> ax = cv2plot(hconcat_resize_min(img, img_opening), cmap="gray")
    """
    handleTypeError(types=[str, int], op=op)
    if isinstance(shape, str):
        handleKeyError(lst=list(OPENCV_MORPHOLOGY_OPERATIONS.keys()), op=op)
        op = OPENCV_MORPHOLOGY_OPERATIONS.get(op)
    if kernel is None:
        kernel = morph_kernel_creator(shape=shape, ksize=ksize)
    transformer = lambda src: cv2.morphologyEx(src, op, kernel)
    return transformer