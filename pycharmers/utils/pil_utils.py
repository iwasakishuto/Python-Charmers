# coding: utf-8
import os
import math
import urllib
import string
import textwrap
from PIL import Image, ImageDraw, ImageFont

from .print_utils import pretty_3quote
from .generic_utils import assign_trbl, handleKeyError, flatten_dual
from ._colorings import toBLUE, toGREEN

def pilread(img=None, path=None):
    """Opens and identifies the given image file.
    
    Args:
        img (PIL.Image) : PIL Image object
        path (str)      : Path or URL to image file.
        
    Returns
        img (PIL.Image) : PIL Image object
        
    Examples:
        >>> from pycharmers.utils import pilread
        >>> img = pilread(img=None, path="https://iwasakishuto.github.io/Python-Charmers/_static/favicon.png")
        >>> img == pilread(img=img, path=None)
        True
    """
    if path is not None:
        if isinstance(path, str) and (not os.path.exists(path)):
            with urllib.request.urlopen(path) as web_file:
                img = Image.open(web_file)
        else:
            img = Image.open(path)
    return img

def roughen_img(img=None, path=None, rrate=5):
    """Roughen the Image.
    
    Args:
        img (PIL.Image) : image file.
        path (str)      : Path or URL to image file.
        rrate (float)   : Reduction rate. 

    Returns
        img (PIL.Image) : Roughened PIL Image object

    Examples:
        >>> from pycharmers.utils import roughen_img, pilread
        >>> img = pilread(path="https://iwasakishuto.github.io/Python-Charmers/_static/favicon.png")
        >>> roughened_img = roughen_img(img=img, rrate=5)
        >>> img.size == roughened_img.size
        True
    """
    img = pilread(img=img, path=path)
    img_size_origin = img._size
    img_size_small  = [int(s/rrate) for s in img_size_origin]
    return img.resize(size=img_size_small).resize(size=img_size_origin)

def draw_text_in_pil(text, img=None, ttfontname=None,
                     img_size=(250, 250), text_width=None, 
                     fontsize=16, fontwidth=None, fontheight=None,
                     margin=10, line_height=None, drop_whitespace:bool=False,
                     bgRGB=(255,255,255), textRGB=(0,0,0), mode="RGB",
                     ret_position="line",
                     **kwargs):
    """Draw text in ``PIL.Image`` object.

    Args:
        text (str)             : Text to be drawn to ``img``.
        img (PIL.Image)        : The image to draw in. If this argment is ``None``, img will be created using ``img_size`` and ``bgRGB`` arguments.
        ttfontname (str)       : A filename or file-like object containing a TrueType font. If the file is not found in this filename, the loader may also search in other directories, such as the ``fonts/`` directory on Windows or ``/Library/Fonts/`` , ``/System/Library/Fonts/`` and ``~/Library/Fonts/`` on macOS.
        img_size (tuple)       : The image size.
        text_width (int)       : The length of characters in one line.
        fontsize (int)         : The requested size, in points.
        fontwidth (int)        : The font width. (If not given, automatically calculated.)
        fontheight (int)       : The font height. (If not given, automatically calculated.)
        margin (int)           : The margin size.
        line_height (int)      : The line height. If not specify, use ``font.getsize(string.ascii_letters)``
        drop_whitespace (bool) : If ``True``, whitespace at the beginning and ending of every line. Defaults to ``False``.
        bgRGB (tuple)          : The color of background image. (RGB)
        textRGB (tuple)        : The color of text. (RGB)
        mode (str)             : Optional mode to use for color values.
        ret_position (str)     : Type of the position of next text to be returned. Please choose from ``["line", "word"]``. Defaults to ``"line"``.
        \*\*kwargs (dict)      : Specify ``margin_top`` , ``margin_right`` , ``margin_bottom`` , ``margin_left`` .

    Returns:
        tuple (PIL.Image, pos): img, Position of next text ( ``x`` , ``y`` ).
    
    Example:
        >>> from pycharmers.utils import draw_text_in_pil
        >>> img, y = draw_text_in_pil("Hello World!!")
        >>> img.save("sample.png")
    """
    if img is None:
        img = Image.new(mode=mode, size=img_size, color=bgRGB)
    else:
        img_size = img.size
    if ttfontname is None:
        raise TypeError(*pretty_3quote(f"""
            Please define the {toGREEN('ttfontname')}. If you dont't know where the font file is, check the
            * {toBLUE('fonts/')} directory on Windows
            * {toBLUE('/Library/Fonts/')}, {toBLUE('/System/Library/Fonts/')}, or {toBLUE('~/Library/Fonts/')} on macOS
            or, use {toGREEN('pycharmers.utils.generic_urils.get_random_ttfontname')} to get the path to a random font file.
            """))
    handleKeyError(lst=["line", "word"], ret_position=ret_position)
    
    iw,ih = img_size
    kwargs["margin"] = margin
    mt,mr,mb,ml = assign_trbl(data=kwargs, name="margin")
    ml = kwargs.get("x", ml); mt = kwargs.get("y", mt)
    
    font = ImageFont.truetype(font=ttfontname, size=fontsize)
    fw,fh = font.getsize(string.ascii_letters)
    fw = fontwidth or fw//len(string.ascii_letters)
    fh = fontheight or line_height or fh
    
    max_text_width = (iw-(mr+ml))//fw
    text_width = text_width or max_text_width
    wrapped_lines = flatten_dual([textwrap.wrap(
        text=t, width=text_width, drop_whitespace=drop_whitespace
    ) for t in text.split("\n")])
    max_text_height = (ih-(mt+mb))//fh
    
    if len(textRGB)>3 and mode=="RGBA":
        text_canvas = Image.new(mode=mode, size=img.size, color=(255,255,255,0))
        draw = ImageDraw.Draw(im=text_canvas, mode=mode)
    else:
        draw = ImageDraw.Draw(im=img, mode=mode)

    if len(wrapped_lines)>0:
        for i,line in enumerate(wrapped_lines):
            y = i*fh+mt
            draw.multiline_text((ml, y), line, fill=textRGB, font=font)
    else:
        y = mt; line=[]
    if ret_position == "line":
        pos = (ml,y+fh)
    elif ret_position == "word":
        pos = (fw*len(line)+ml,y)

    if len(textRGB)>3 and mode=="RGBA":
        img = Image.alpha_composite(im1=img, im2=text_canvas).convert(mode)
    return img, pos

def draw_cross(img, size, width=5, fill_color=(255,0,0,255), outline=None, color_mode="RGBA", margin=0, **kwargs):
    """Draw Cross Mark.
    
    Args:
        img (PIL.Image)    : Pillow Image.
        size (int/tuple)   : Cross mark size. (width,Height)
        width (int)        : The width of the cross mark.
        fill_color (tuple) : The color in the line.
        outline (tuple)    : The color of the edge of the line.
        color_mode (str)   : Color Mode (ex. ``"RGBA"`` , ``"P"`` )
        margin (int/list)  : Specify the position. 
        \*\*kwargs (dict)  : Specify the individual margin ( ``margin_top`` , ``margin_right`` )
        
    Examples:
        >>> from PIL import Image
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG
        >>> from pycharmers.utils import draw_cross
        >>> img = Image.open(SAMPLE_LENA_IMG)
        >>> draw_cross(img=img, size=200, width=10)
        >>> draw_cross(img=img, size=(100,200), width=10, outline=(0,255,0))
    """
    ori_mode = img.mode
    img = img.convert(color_mode)
    draw = ImageDraw.Draw(img)
    W,H = img.size
    
    kwargs["margin"] = margin
    mt,mr,mb,ml = assign_trbl(data=kwargs, name="margin")
    if hasattr(size, "__len__"):
        sx,sy = size[:2]
    else:
        sx = sy = size
    sx /= 2; sy /= 2
    angle = math.atan(sy/sx)
    cx = (W-ml-mr)//2+ml
    cy = (H-mt-mb)//2+mt
    dx = (width/2) * math.sin(angle)
    dy = (width/2) * math.cos(angle)
    
    for xy in [
        ((cx-sx-dx,cy-sy+dy),(cx+sx-dx,cy+sy+dy),(cx+sx+dx,cy+sy-dy),(cx-sx+dx,cy-sy-dy)),
        ((cx+sx-dx,cy-sy-dy),(cx+sx+dx,cy-sy+dy),(cx-sx+dx,cy+sy+dy),(cx-sx-dx,cy+sy-dy))
    ]:
        draw.polygon(
            xy=xy,
            fill=fill_color,
            outline=outline,
        )
    return img.convert(ori_mode)

def draw_frame(img, width=10, border_color=(255,255,255), is_radius=True):
    """Draw Frame with Image.
    
    Args:
        img (PIL.Image)      : Pillow Image.
        width (int)          : The width of the border.
        border_color (tuple) : The color in the border.
        is_radius (bool)     : Whether to round the corners.
        
    Examples:
        >>> from PIL import Image
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG
        >>> from pycharmers.utils import draw_frame
        >>> img = Image.open(SAMPLE_LENA_IMG)
        >>> draw_frame(img=img, width=10)
    """
    w,h = img.size
    hw = width//2
    
    kwargs = {"fill": border_color, "width": width}
    if is_radius:
        l,r,t,b = (width, w-width, width, h-width)
    else:
        l,r,t,b = (0,w,0,h)
    
    draw = ImageDraw.Draw(img)
    for xy in [(l,hw-1,r,hw-1),(w-hw,t,w-hw,b),(r,h-hw,l,h-hw),(hw,b,hw,t)]:
        draw.line(xy=xy, **kwargs)
        
    if is_radius:
        draw.arc((0, 0, width*2, width*2), start=180, end=270,   **kwargs)
        draw.arc((w-width*2, 0, w, width*2), start=270, end=360, **kwargs)
        draw.arc((w-width*2, h-width*2, w, h), start=0, end=90,  **kwargs)
        draw.arc((0, h-width*2, width*2, h), start=90, end=180,  **kwargs)    
    
    return img