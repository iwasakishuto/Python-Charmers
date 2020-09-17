import cv2

# cv2.morphologyEx(img, OP, kernel)
MORPHOLOGY_TRANSFORMER_CREATOR = {
    "opening"  : cv2.MORPH_OPEN,
    "closing"  : cv2.MORPH_CLOSE,
    "gradient" : cv2.MORPH_GRADIENT,
    "tophat"   : cv2.MORPH_TOPHAT,
    "blackhat" : cv2.MORPH_BLACKHAT,
    "hitmiss"  : cv2.MORPH_HITMISS,
}
MORPHOLOGY_TRANSFORMER_ALGORITHMS = list(MORPHOLOGY_TRANSFORMER_CREATOR.keys())
# cv.getStructuringElement(shape, size)
MORPH_KERNEL_SHAPE = {
    "cross"  : cv2.MORPH_CROSS,
    "dilate" : cv2.MORPH_DILATE,
    "erode"  : cv2.MORPH_ERODE,
    "open"   : cv2.MORPH_OPEN,
}
MORPH_KERNEL_TYPES = list(MORPH_KERNEL_SHAPE.keys())

def morph_kernel_creator(shape="erode", size=(5,5)):
    if isinstance(shape, str):
        shape = MORPH_KERNEL_SHAPE.get(shape)
    return cv2.getStructuringElement(shape, tuple(size))

def morph_transformer_creator(op, kernel=None, shape="erode", size=(5,5)):
    """
    @param op Type of a morphological operation, see #MorphTypes
    """
    if isinstance(op, str):
        op = MORPHOLOGY_TRANSFORMER_CREATOR.get(op)
    if kernel is None:
        kernel = morph_kernel_creator(shape=shape, size=size)
    transformer = lambda src: cv2.morphologyEx(src, op, kernel)
    return transformer