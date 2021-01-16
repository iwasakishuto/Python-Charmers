# coding: utf-8
def test_cascade_creator():
    from pycharmers.opencv import SAMPLE_LENA_IMG, cv2read_mpl, cv2plot, cascade_creator, draw_bboxes_xywh
    cascade = cascade_creator(cascade="haarcascades:haarcascade_frontalface_alt2")
    gray = cv2read_mpl(SAMPLE_LENA_IMG, 0)
    for bbox in cascade.detectMultiScale(gray):
        draw_bboxes_xywh(
            frame=gray, bboxes=bbox
        )
    ax = cv2plot(gray)

def test_cascade_detection_create():
    import cv2
    from pycharmers.opencv import SAMPLE_LENA_IMG, cv2read_mpl, cv2plot, cascade_detection_create, draw_bboxes_ltrb
    cascade_detection = cascade_detection_create(cascade="haarcascades:haarcascade_frontalface_alt2")
    img = cv2.cvtColor(cv2.imread(SAMPLE_LENA_IMG), cv2.COLOR_BGR2RGB) 
    for bbox in cascade_detection(img):
        draw_bboxes_ltrb(frame=img, bboxes=bbox)
    ax = cv2plot(img)

