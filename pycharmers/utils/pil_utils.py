# coding: utf-8
import os
import string
import textwrap
from PIL import Image, ImageDraw, ImageFont

def draw_text(text, img=None, ttfontname=os.listdir("/System/Library/Fonts")[0],
              img_size=(250, 250), text_width=None, fontsize=16, margin=10,
              bgRGB=(255,255,255), textRGB=(0,0,0), **kwargs):
    """Draw text in ``PIL.Image`` object.

    Args:
        text (str)       : Text to be drawn to ``img``.
        img (PIL.Image)  : The image to draw in. If this argment is ``None``, img will be created using ``img_size`` and ``bgRGB`` arguments.
        ttfontname (str) : A filename or file-like object containing a TrueType font.
        img_size (tuple) : The image size.
        text_width (int) : The length of characters in one line.
        fontsize (int)   : The requested size, in points.
        margin (int)     : The margin size.
        bgRGB (tuple)    : The color of background image. (RGB)
        textRGB (tuple)  : The color of text. (RGB)

    Returns:
        tuple (PIL.Image, int): img, Length from top to bottom text line.
    
    Example:
        >>> from pycharmers.utils import take_centers
        >>> img, y = draw_text("Hello World!!")
        >>> img.save("sample.png")
    """
    if img is None:
        img = Image.new(mode="RGB", size=img_size, color=bgRGB)
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