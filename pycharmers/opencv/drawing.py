#coding: utf-8
import re
import cv2
import math
import numpy as np

from ..utils.generic_utils import handleKeyError
from ..matplotlib.cmaps import FAMOUS_COLOR_PALETTES, color_dict_create
from ..matplotlib.layout import FigAxes_create, clear_grid

SUPPORTED_COORD_TYPES = ["xywh", "ltrb"]
cv2BLACK   = (0,     0,   0)
cv2RED     = (0,     0, 255)
cv2GREEN   = (0,   128,   0)
cv2YELLOW  = (0,   255, 255)
cv2BLUE    = (255,   0,   0)
cv2MAGENTA = (255,   0, 255)
cv2CYAN    = (255, 255,   0)
cv2WHITE   = (255, 255, 255)

def convert_coords(bbox, to_type, from_type=""):
    """Convert coordinates::

               [OpenCV]                  [YOLO]
         (x,y)---------(x+w,y)    (l,t)----------(r,t)
           |              |         |              |
           |              |         |              |
           |              |         |              |
        (x,y+h)-------(x+w,y+h)   (l,b)----------(r,b)
                [xywh]                   [ltrb]

    Args:
        bbox (tuple)  : Bounding Box coordinates.
        to_type (str) : coordinate type.

    Examples:
        >>> from pycharmers.opencv import convert_coords
        >>> xywh = (120,250,60,80)
        >>> ltrb = convert_coords(bbox=xywh, to_type="ltrb")
        >>> xywh = convert_coords(bbox=ltrb, to_type="xywh")
    """
    handleKeyError(lst=SUPPORTED_COORD_TYPES, to_type=to_type)
    if from_type!=to_type:
        a,b,c,d = bbox
        if to_type == "xywh":
            a,b,c,d = (a,b,c-a,d-b)
        elif to_type == "ltrb":
            a,b,c,d = (a,b,a+c,b+d)
        bbox = (a,b,c,d)
    return bbox

def draw_bboxes_create(coord_type="xywh"):
    handleKeyError(lst=SUPPORTED_COORD_TYPES, coord_type=coord_type)
    def draw_bboxes(frame, bboxes, infos=None):
        if not hasattr(bboxes[0], "__iter__"):
            bboxes = [bboxes]
        if infos is None:
            infos = [{} for _ in range(len(bboxes))]
        for bbox,info in zip(bboxes, infos):
            color = info.pop("color", (0,255,0))
            text  = info.pop("text", "")
            rectangle_thickness = info.pop("rectangle_thickness", 3)
            l,t,r,b = convert_coords(bbox, to_type="ltrb", from_type=coord_type)
            cv2.rectangle(img=frame, pt1=(l, t), pt2=(r, b), color=color, thickness=rectangle_thickness)
            if len(text)>0:
                draw_text_with_bg(img=frame, text=text, org=(l,t-10), offset=(10, 10), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.5, thickness=2)
        return frame
    dict_infos = '{"color":(255,0,0),"text": "person1"},{"color":(0,255,0),"text": "person2"}'
    draw_bboxes.__doc__ = f"""Drawing Inference results on frame.
    
    Args:
        frame (ndarray) : Image. shape=(H,W,ch)
        bboxes (list)   : Each element is the coordinate (x,y,w,h)
        infos (list)    : Each element is dictionary. (``key`` is ``color``, or ``text``)

    Examples:
        >>> import cv2
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.opencv import draw_bboxes_{coord_type}, cv2read_mpl
        >>> img = cv2read_mpl("path/to/img.png")
        >>> draw_bboxes_{coord_type}(
        ...     frame=img, 
        ...     bboxes=[(120,250,60,80),(220,40,80,100)], 
        ...     infos=[{dict_infos}]
        ... )
        >>> plt.imshow(img)
        >>> plt.show()
    """
    return draw_bboxes

draw_bboxes_xywh = draw_bboxes_create(coord_type="xywh")
draw_bboxes_ltrb = draw_bboxes_create(coord_type="ltrb")

def cv2read_mpl(filename, *flags):
    """loads an image from the specified file and returns it as RGB format.
    
    Args:
        filename (str): Name of file to be loaded.
        flags (int)   : Flags.
    """
    return cv2.cvtColor(cv2.imread(filename, *flags), cv2.COLOR_BGR2RGB) 

def cv2plot(x, ax=None, clear_pos=["l","t","r","b"], cmap=None, is_cv2=False, figkeywargs={}, plotkeywargs={}):
    """Plot Image using OpenCV

    Args:
        x (str/np.ndarray)  : path to an image, or image. (BGR)
        ax (Axes)           : The ``Axes`` instance.
        clear_pos (list)    : Positions to clean a grid
        cmap (str)          : 
        is_cv2 (bool)       : Whether ``x`` is BGR (OpenCV format) or not.
        figkeywargs (dict)  : Keyword arguments for :meth:`FigAxes_create <pycharmers.matplotlib.layout.FigAxes_create>`
        plotkeywargs (dict) : Keyword arguments for ``ax.imshow`` .

    Examples:
        >>> from pycharmers.opencv import cv2plot, SAMPLE_LENA_IMG
        >>> ax = cv2plot(x=SAMPLE_LENA_IMG)
    """
    cmap = cmap or plotkeywargs.pop("cmap", None)
    ax = FigAxes_create(ax=ax, **figkeywargs)[1][0]
    if isinstance(x, str):
        x = cv2read_mpl(x)
    elif is_cv2:
        x = cv2.cvtColor(x, cv2.COLOR_BGR2RGB) 
    ax.imshow(X=x, cmap=cmap, **plotkeywargs)
    ax = clear_grid(ax, pos=clear_pos)
    return ax

def draw_text_with_bg(img, text, org=(10,10), offset=(10, 10),
                      fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                      color=cv2BLACK, bgcolor=cv2WHITE, color_type="css4",
                      thickness=2, **kwargs):
    """Put text with background color.

    Args:
        img (np.ndarray)        : Image.
        text (str)              : Text string to be drawn.
        org (tuple)             : Bottom-left corner of the text string in the image.
        fontFace (int)          : Font type.
        fontScale (int)         : Font scale factor that is multiplied by the font-specific base size.
        color (str/tuple)       : Text color.
        thickness (int)         : Thickness of the lines used to draw a text.
        lineType (int)          : Line type.
        bottomLeftOrigin (bool) : When ``True`, the image data origin is at the bottom-left corner. Otherwise, it is at the top-left corner.
    
    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.opencv import draw_text_with_bg, cv2read_mpl, SAMPLE_LENA_IMG
        >>> img = cv2read_mpl(filename=SAMPLE_LENA_IMG)
        >>> draw_text_with_bg(img=img, offset=(100,-100), text="My name is Shuto")
        >>> plt.imshow(img)
        >>> plt.show()
    """
    if isinstance(color, str):
        color = FAMOUS_COLOR_PALETTES.get(color_type).get(color, cv2BLACK)
    if isinstance(bgcolor, str):
        bgcolor = FAMOUS_COLOR_PALETTES.get(color_type).get(bgcolor, cv2WHITE)

    text_W, text_H = cv2.getTextSize(text=text, fontFace=fontFace, fontScale=fontScale, thickness=thickness)[0]
    text_off_x, text_off_y = offset
    org_x, org_y = org

    box_coords = (
        (org_x          - text_off_x, org_y          + text_off_y), 
        (org_x + text_W + text_off_x, org_y - text_H - text_off_y)
    )
    cv2.rectangle(img, *box_coords, bgcolor, cv2.FILLED)
    cv2.putText(
        img=img, text=text, org=org, fontFace=fontFace,
        fontScale=fontScale, color=color, thickness=thickness, **kwargs
    )

def plot_cv2fontFaces(bgcolor=(50,50,50), cmap="Pastel1"):
    """Plot All ``fontFace`` supported by OpenCV.

    Args:
        bgcolor (tuple) : background color (RGB)
        cmap (str)      : The name of a color map known to ``matplotlib``

    Examples:
        >>> from pycharmers.opencv import plot_cv2fontFaces
        >>> plot_cv2fontFaces()
    """
    i=0; img = np.full(shape=(400,1400,3), fill_value=bgcolor, dtype=np.uint8)
    color_dict = color_dict_create(keys=range(8), cmap=cmap, max_val=255)
    for name,val in cv2.__dict__.items():
        m = re.match(pattern=r"^FONT_(?!.*ITALIC$).+$", string=name)
        if m:
            cv2.putText(img=img, text=f"{val:>02} {name}", org=(20,  35+50*i), fontScale=1, color=color_dict[i%8], fontFace=val)
            cv2.putText(img=img, text=f"{val | cv2.FONT_ITALIC:>02} {name}", org=(720, 35+50*i), fontScale=1, color=color_dict[i%8], fontFace=val | cv2.FONT_ITALIC)
            i+=1
    ax = cv2plot(img, figkeywargs={"figsize": (14,49)}, is_cv2=False)
    ax.set_title("OpenCV fontFace [left: normal, right: FONT_ITALICK]", size=20)
    return ax