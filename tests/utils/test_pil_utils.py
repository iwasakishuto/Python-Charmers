# coding: utf-8
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

