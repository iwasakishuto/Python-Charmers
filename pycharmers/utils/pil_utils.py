# coding: utf-8
import os
import urllib
import string
import textwrap
from PIL import Image, ImageDraw, ImageFont

from .print_utils import pretty_3quote
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
                     img_size=(250, 250), text_width=None, fontsize=16, margin=10,
                     bgRGB=(255,255,255), textRGB=(0,0,0), **kwargs):
    """Draw text in ``PIL.Image`` object.

    Args:
        text (str)       : Text to be drawn to ``img``.
        img (PIL.Image)  : The image to draw in. If this argment is ``None``, img will be created using ``img_size`` and ``bgRGB`` arguments.
        ttfontname (str) : A filename or file-like object containing a TrueType font. If the file is not found in this filename, the loader may also search in other directories, such as the ``fonts/`` directory on Windows or ``/Library/Fonts/`` , ``/System/Library/Fonts/`` and ``~/Library/Fonts/`` on macOS.
        img_size (tuple) : The image size.
        text_width (int) : The length of characters in one line.
        fontsize (int)   : The requested size, in points.
        margin (int)     : The margin size.
        bgRGB (tuple)    : The color of background image. (RGB)
        textRGB (tuple)  : The color of text. (RGB)

    Returns:
        tuple (PIL.Image, int): img, Length from top to bottom text line.
    
    Example:
        >>> from pycharmers.utils import draw_text_in_pil
        >>> img, y = draw_text_in_pil("Hello World!!")
        >>> img.save("sample.png")
    """
    if img is None:
        img = Image.new(mode="RGB", size=img_size, color=bgRGB)
    if ttfontname is None:
        raise TypeError(*pretty_3quote(f"""
            Please define the {toGREEN('ttfontname')}. If you dont't know where the font file is, check the 
            * {toBLUE('fonts/')} directory on Windows
            * {toBLUE('/Library/Fonts/')}, {toBLUE('/System/Library/Fonts/')}, or {toBLUE('~/Library/Fonts/')} on macOS
            """))
    draw = ImageDraw.Draw(im=img, mode="RGB")
    
    iw,ih = img_size
    mt = kwargs.pop("margin_top",    margin)
    mr = kwargs.pop("margin_right",  margin)
    mb = kwargs.pop("margin_bottom", margin)
    ml = kwargs.pop("margin_left",   margin)
    
    font = ImageFont.truetype(font=ttfontname, size=fontsize)
    fw,fh = font.getsize(string.ascii_letters)
    fw = fw//len(string.ascii_letters)
    
    max_text_width = (iw-(mr+ml))//fw
    text_width = text_width or max_text_width
    wrapped_lines = textwrap.wrap(text=text, width=text_width)    
    max_text_height = (ih-(mt+mb))//fh
                
    for i,line in enumerate(wrapped_lines):
        y = i*fh+mt
        draw.multiline_text((ml, y), line, fill=textRGB, font=font)
    return img, (y+fh)