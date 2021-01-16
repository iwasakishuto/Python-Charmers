# coding: utf-8
def test_convert_coords():
    from pycharmers.opencv import convert_coords
    xywh = (120,250,60,80)
    ltrb = convert_coords(bbox=xywh, to_type="ltrb")
    xywh = convert_coords(bbox=ltrb, to_type="xywh")

def test_cv2plot():
    from pycharmers.opencv import cv2plot, SAMPLE_LENA_IMG
    ax = cv2plot(x=SAMPLE_LENA_IMG)

def test_draw_bboxes_ltrb():
    import cv2
    import matplotlib.pyplot as plt
    from pycharmers.opencv import draw_bboxes_ltrb, cv2read_mpl
    img = cv2read_mpl("path/to/img.png")
    draw_bboxes_ltrb(
        frame=img, 
        bboxes=[(120,250,60,80),(220,40,80,100)], 
        infos=[{"color":(255,0,0),"text": "person1"},{"color":(0,255,0),"text": "person2"}]
    )
    plt.imshow(img)
    plt.show()

def test_draw_bboxes_xywh():
    import cv2
    import matplotlib.pyplot as plt
    from pycharmers.opencv import draw_bboxes_xywh, cv2read_mpl
    img = cv2read_mpl("path/to/img.png")
    draw_bboxes_xywh(
        frame=img, 
        bboxes=[(120,250,60,80),(220,40,80,100)], 
        infos=[{"color":(255,0,0),"text": "person1"},{"color":(0,255,0),"text": "person2"}]
    )
    plt.imshow(img)
    plt.show()

def test_draw_text_with_bg():
    import matplotlib.pyplot as plt
    from pycharmers.opencv import draw_text_with_bg, cv2read_mpl, SAMPLE_LENA_IMG
    img = cv2read_mpl(filename=SAMPLE_LENA_IMG)
    draw_text_with_bg(img=img, offset=(100,-100), text="My name is Shuto")
    plt.imshow(img)
    plt.show()

def test_plot_cv2fontFaces():
    from pycharmers.opencv import plot_cv2fontFaces
    plot_cv2fontFaces()

