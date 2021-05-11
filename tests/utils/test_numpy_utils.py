# coding: utf-8
def test_confusion_matrix():
    from pycharmers import confusion_matrix
    y_true = [2, 0, 2, 2, 0, 1]
    y_pred = [0, 0, 2, 2, 0, 2]
    confusion_matrix(y_true, y_pred)
    # array([[2, 0, 0],
    #     [0, 0, 1],
    #     [1, 0, 2]])
    # In the binary case, we can extract true positives, etc as follows:
    tn, fp, fn, tp = confusion_matrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
    (tn, fp, fn, tp)
    # (0, 2, 1, 1)

def test_fill_between_angle():
    import numpy as np
    from PIL import Image
    from pycharmers.utils import fill_between_angle
    arr = np.zeros(shape=(100,100,3)).astype(np.uint8)
    flag = fill_between_angle(arr, s=30, e=120, is_radian=False)
    Image.fromarray(np.where(flag, arr, 255)) 

def test_replaceArray():
    import cv2
    import numpy as np
    from pycharmers.opencv import SAMPLE_LENA_IMG, cv2plot
    from pycharmers.utils import replaceArray
    img = cv2.imread(SAMPLE_LENA_IMG)
    img = replaceArray(img, old=[77, 66, 176], new=[0,0,0]).astype(np.uint8)
    cv2plot(img, is_cv2=True)

