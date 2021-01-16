# coding: utf-8
def test_choose_text_color():
    from pycharmers.utils import choose_text_color
    from pycharmers.opencv import (cv2BLACK, cv2RED, cv2GREEN, cv2YELLOW, cv2BLUE, cv2MAGENTA, cv2CYAN, cv2WHITE) 
    colors = locals().copy()
    for name,color in colors.items():
        if name.startswith("cv2") and isinstance(color, tuple):
            print(f"{name.lstrip('cv2'):<7}: {str(color):<15} -> {choose_text_color(color=color, max_val=255, is_bgr=True)}")        

def test_detect_color_code_type():
    from pycharmers.utils import detect_color_code_type
    detect_color_code_type("#FFFFFF")
    # 'hex'
    detect_color_code_type((255,255,255))
    # 'rgb'
    detect_color_code_type((0,0,0,1))
    # 'rgba'

def test_generateLightDarks():
    from pycharmers.utils import generateLightDarks
    generateLightDarks(color=(245,20,25), variation=3, diff=10)
    # [(235, 10, 15), (245, 20, 25), (255, 30, 35)]
    generateLightDarks(color=(245, 20, 25), variation=3, diff=-10)
    # [(225, 0, 5), (235, 10, 15), (245, 20, 25)]

def test_toHEX():
    from pycharmers.utils import toHEX
    toHEX("#FFFFFF")
    # #FFFFFF
    toHEX((255, 255, 255), max_val=255)
    # #FFFFFF
    toHEX((1, 1, 1, 1), max_val=1)
    # #FFFFFF


def test_toRGB():
    from pycharmers.utils import toRGB
    toRGB("#FFFFFF")
    # (1.0, 1.0, 1.0)
    toRGB((255, 255, 255), max_val=255)
    # (255, 255, 255)
    toRGB((1, 1, 1, 1), max_val=1)
    # (1.0, 1.0, 1.0)


def test_toRGBA():
    from pycharmers.utils import toRGBA
    toRGBA("#FFFFFF")
    # (1.0, 1.0, 1.0, 1)
    toRGBA((255, 255, 255), max_val=255)
    # (255, 255, 255, 1)
    toRGBA((1, 1, 1, 1), max_val=1)
    # (1, 1, 1, 1)


