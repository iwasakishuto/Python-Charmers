# coding: utf-8
def test_background_subtractor_create():
    import cv2
    from pycharmers.opencv import background_subtractor_create
    mog = background_subtractor_create("mog")
    mog
    # # <BackgroundSubtractorMOG2 0x12a165a30>
    mog = background_subtractor_create(cv2.createBackgroundSubtractorMOG2())
    mog
    # # <BackgroundSubtractorMOG2 0x12a1658d0>
    mog = background_subtractor_create(cv2.BackgroundSubtractorMOG2)
    # TypeError: identifier must be one of ['cv2.BackgroundSubtractor', 'str'], not typ
