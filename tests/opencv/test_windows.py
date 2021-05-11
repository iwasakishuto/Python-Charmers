# coding: utf-8
def test_FrameWindow():
    import cv2
    from pycharmers.opencv import FrameWindow, SAMPLE_VTEST_VIDEO
    window = FrameWindow(SAMPLE_VTEST_VIDEO)
    while True:
        key = cv2.waitKey(0)
        is_break = window.recieveKey(key)
        if is_break:
            break
    cv2.destroyAllWindows()

def test_RealTimeWindow():
    import cv2
    from pycharmers.opencv import RealTimeWindow
    window = RealTimeWindow()
    while True:
        key = cv2.waitKey(0)
        is_break = window.recieveKey(key)
        if is_break:
            break
    cv2.destroyAllWindows()

def test_TrackingWindow():
    import cv2
    from pycharmers.opencv import TrackingWindow, SAMPLE_VTEST_VIDEO
    window = TrackingWindow(path=SAMPLE_VTEST_VIDEO, tracker="boosting", coord_type="xywh")
    while True:
        key = cv2.waitKey(0)
        is_break = window.recieveKey(key)
        if is_break:
            break
    cv2.destroyAllWindows()

def test_cv2key2chr():
    from pycharmers.opencv import cv2key2chr
    import cv2
    import numpy as np
    from pycharmers.opencv import cv2key2chr
     
    winname = "cv2key2chr"
    image = np.random.randint(low=0, high=255, size=(200,200,3), dtype=np.uint8)
    while True:
        key = cv2.waitKey(1)
        cv2.imshow(winname=winname, mat=image)
        if key!=-1: print(key, cv2key2chr(key))
        if key==27: break
    cv2.destroyWindow(winname=winname)

def test_cvKeys():
    from pycharmers.opencv import cvKeys, DEFAULT_CV_KEYS
    cvKey = cvKeys(**DEFAULT_CV_KEYS)
    cvKey.MOVING_LEFT_KEY
    # 'h'
    cvKey.MOVING_LEFT_KEY_ORD
    # 104
    cvKey.MOVING_KEYS
    # ['h', 'l', 'j', 'k']
    cvKey.MOVING_KEYS_ORD
    # [104, 108, 106, 107]
    cvKey.ALL_KEYS
    # ['i', 'q', '<delete>', '<enter>', 'h', 'l', 'j', 'k', '+', '-', 'f', 'o']
    cvKey.ALL_KEYS_ORD
    # [105, 113, 8, 13, 104, 108, 106, 107, 43, 45, 102, 111]


def test_cvWindow():
    import cv2
    from pycharmers.opencv import cvWindow
    window = cvWindow()
    while True:
        key = cv2.waitKey(0)
        is_break = window.recieveKey(key)
        if is_break:
            break
    cv2.destroyAllWindows()

def test_wait_for_choice():
    import cv2
    from pycharmers.opencv import wait_for_choice, SAMPLE_LENA_IMG
    cv2.imshow("Lena", cv2.imread(SAMPLE_LENA_IMG))
    val = wait_for_choice(*list("ltrb"))
    cv2.destroyAllWindows()

def test_wait_for_input():
    import cv2
    from pycharmers.opencv import wait_for_input, SAMPLE_LENA_IMG
    cv2.imshow("Lena", cv2.imread(SAMPLE_LENA_IMG))
    val = wait_for_input()
    cv2.destroyAllWindows()

