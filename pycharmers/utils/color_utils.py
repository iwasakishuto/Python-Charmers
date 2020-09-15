#coding: utf-8
from .generic_utils import handleTypeError

SUPPORTED_COLOR_CODES = ["hex", "rgb", "rgba"]

def detect_color_code_type(color):
    """Detect Color Code type

    Args:
        color (tuple / str): color code.

    Examples:
        >>> from pycharmers.utils import detect_color_code_type
        >>> detect_color_code_type("#FFFFFF")
        'hex'
        >>> detect_color_code_type((255,255,255))
        'rgb'
        >>> detect_color_code_type((0,0,0,1))
        'rgba'
    """
    handleTypeError(types=[str, tuple, list], color=color)
    if isinstance(color, str):
        color_code = "hex"
    elif isinstance(color, tuple) or isinstance(color, list):
        color_code = {
            3: "rgb",
            4: "rgba",
        }.get(len(color))
    return color_code

def hex2rgb(hex, max_val=1):
    """Convert color code from ``hex`` to ``rgb``"""
    return tuple([int(hex[-6:][i*2:(i+1)*2], 16)/255*max_val for i in range(3)])

def hex2rgba(hex, max_val=1):
    """Convert color code from ``hex`` to ``rgba``"""
    return rgb2rgba(rgb=hex2rgb(hex=hex[-6:], max_val=max_val), max_val=max_val)

def rgb2hex(rgb, max_val=1):
    """Convert color code from ``rgb`` to ``hex``"""
    return "#"+"".join([format(int(255/max_val*e), '02x') for e in rgb]).upper()

def rgb2rgba(rgb, max_val=1):
    """Convert color code from ``rgb`` to ``rgba``"""
    return (*rgb, 1)

def rgba2hex(rgba, max_val=1):
    """Convert color code from ``rgba`` to ``hex``"""
    return rgb2hex(rgb=rgba2rgb(rgba=rgba, max_val=max_val), max_val=max_val)

def rgba2rgb(rgba, max_val=1):
    """Convert color code from ``rgba`` to ``rgb``"""
    alpha = rgba[-1]
    rgb = rgba[:-1]
    type_ = int if max_val==255 else float
    # compute the color as alpha against white
    return tuple([type_(alpha*e+(1-alpha)*max_val) for e in rgb])

def _do_nothing(color, max_val=1):
    return color

def _toColorCode_create(to_color_code):
    def toColorCode(color, max_val=1):
        color_code = detect_color_code_type(color=color)
        return {
            color_code: globals().get(f"{color_code}2{to_color_code.lower()}", _do_nothing) 
            for color_code in SUPPORTED_COLOR_CODES
        }.get(color_code)(color, max_val=max_val)
    
    toColorCode.__doc__ = f"""Convert color code to {to_color_code.upper()}

    Args:
        color (tuple / str): color code.
        
    Examples:
        >>> from pycharmers.utils import to{to_color_code.upper()}
        >>> to{to_color_code.upper()}("#FFFFFF")
        {toColorCode("#FFFFFF")}
        >>> to{to_color_code.upper()}((255, 255, 255), max_val=255)
        {toColorCode((255, 255, 255), max_val=255)}
        >>> to{to_color_code.upper()}((1, 1, 1, 1), max_val=1)
        {toColorCode((1, 1, 1, 1), max_val=1)}

    """
    return toColorCode

toHEX  = _toColorCode_create("hex")
toRGB  = _toColorCode_create("rgb")
toRGBA = _toColorCode_create("rgba")

def choose_text_color(color, max_val=1):
    """Select an easy-to-read text color from the given color.

    Args:
        color (tuple / str): color code.

    References: 
        `WCAG <https://www.w3.org/TR/WCAG20/>`_

    Examples:
        >>> from pycharmers.utils import choose_text_color
        >>> choose_text_color(color=(  0,   0,   0), max_val=255)
        (255, 255, 255)
        >>> choose_text_color(color=(  0,   0, 255), max_val=255)
        (255, 255, 255)
        >>> choose_text_color(color=(  0, 255,   0), max_val=255)
        (0, 0, 0)
        >>> choose_text_color(color=(  0, 255, 255), max_val=255)
        (0, 0, 0)
        >>> choose_text_color(color=(255,   0,   0), max_val=255)
        (0, 0, 0)
        >>> choose_text_color(color=(255,   0, 255), max_val=255)
        (0, 0, 0)
        >>> choose_text_color(color=(255, 255,   0), max_val=255)
        (0, 0, 0)
        >>> choose_text_color(color=(255, 255, 255), max_val=255)
        (0, 0, 0)

    """
    color_code = detect_color_code_type(color=color)
    rgb = toRGB(color=color)

    R,G,B = [e/max_val for e in rgb]
    # Relative Brightness BackGround.
    Lbg = 0.2126*R + 0.7152*G + 0.0722*B

    Lw = 1 # Relative Brightness of White
    Lb = 0 # Relative Brightness of Black

    Cw = (Lw + 0.05) / (Lbg + 0.05)
    Cb = (Lbg + 0.05) / (Lb + 0.05)
    text_rgb = (0,0,0) if Cb>Cw else (max_val,max_val,max_val)
    return {
        "rgb"  : _do_nothing,
        "hex"  : rgb2hex,
        "rgba" : _do_nothing,
    }.get(color_code)(text_rgb, max_val=max_val)