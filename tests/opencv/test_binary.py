# coding: utf-8
def test_binarizer_creator():
    import cv2
    from pycharmers.opencv import binarizer_creator, SAMPLE_LENA_IMG, vconcat_resize_min, cv2plot
    from pycharmers.opencv.binary import OPENCV_BINARYZATIONS
    gray = cv2.imread(SAMPLE_LENA_IMG, 0)
    images = [gray]
    images.extend([binarizer_creator(key)(gray) for key in OPENCV_BINARYZATIONS.keys()])
    ax = cv2plot(vconcat_resize_min(*images), cmap="binary", figkeywargs={"figsize": (10,10)})

def test_findBiggestContour():
    import cv2
    from pycharmers.opencv import findBiggestContour, SAMPLE_LENA_IMG
    img_gray = cv2.imread(SAMPLE_LENA_IMG, 0)
    img_th = cv2.Canny(img_gray, 100, 100)
    contours, hierarchy = cv2.findContours(image=img_th, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)
    biggest, max_area = findBiggestContour(contours, eta=0.2)
    max_area
    # 0 # There is no closed countour.

