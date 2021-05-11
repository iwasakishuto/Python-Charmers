# coding: utf-8
def test_draw_cross():
    from PIL import Image
    from pycharmers.opencv import SAMPLE_LENA_IMG
    from pycharmers.utils import draw_cross
    img = Image.open(SAMPLE_LENA_IMG)
    draw_cross(img=img, size=200, width=10)
    draw_cross(img=img, size=(100,200), width=10, outline=(0,255,0))

def test_draw_frame():
    from PIL import Image
    from pycharmers.opencv import SAMPLE_LENA_IMG
    from pycharmers.utils import draw_frame
    img = Image.open(SAMPLE_LENA_IMG)
    draw_frame(img=img, width=10)

def test_pilread():
    from pycharmers.utils import pilread
    img = pilread(img=None, path="https://iwasakishuto.github.io/Python-Charmers/_static/favicon.png")
    img == pilread(img=img, path=None)
    # True

def test_roughen_img():
    from pycharmers.utils import roughen_img, pilread
    img = pilread(path="https://iwasakishuto.github.io/Python-Charmers/_static/favicon.png")
    roughened_img = roughen_img(img=img, rrate=5)
    img.size == roughened_img.size
    # True

