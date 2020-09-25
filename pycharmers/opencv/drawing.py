#coding: utf-8
import cv2
import math

from ..utils.generic_utils import handleKeyError
from ..matplotlib.cmaps import COLOR_WHITE, COLOR_BLACK, FAMOUS_COLOR_PALETTES
from ..matplotlib.layout import FigAxes_create, clear_grid

SUPPORTED_COORD_TYPES = ["xywh", "ltrb"]

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
        if not isinstance(bboxes, list):
            bboxes = [bboxes]
        if infos is None:
            infos = [{} for _ in range(len(bboxes))]
        for bbox,info in zip(bboxes, infos):
            color = info.pop("color", (0,255,0))
            text  = info.pop("text", "")
            l,t,r,b = convert_coords(bbox, to_type="ltrb", from_type=coord_type)
            cv2.rectangle(img=frame, pt1=(l, t), pt2=(r, b), color=color, thickness=1)
            cv2.putText(frame, text, (l,t), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), thickness=1)
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

def cv2plot(x, ax=None, clear_pos=list("ltrb"), cmap=None, **kwargs):
    """Plot Image using OpenCV

    Args:
        x (str/np.ndarray) : path to an image, or image. (BGR)
        ax (Axes)          : The ``Axes`` instance.
        clear_pos (list)   : Positions to clean a grid
        **kwargs           : 

    Examples:
        >>> from pycharmers.opencv.cv2plot
        >>> ax = cv2plot(x="path/to/image.png")
    """
    fig, ax = FigAxes_create(ax=ax)
    if isinstance(x, str):
        x = cv2read_mpl(x)
    ax.imshow(X=x, **kwargs)
    ax = clear_grid(ax, pos=clear_pos)
    return ax

def draw_text_with_bg(img, text, org=(10,10), offset=(10, -25),
                      fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                      color=COLOR_BLACK, bgcolor=COLOR_WHITE, color_type="css4",
                      thickness=2, **kwargs):
    """Put text with background color.

    Args:
        img (np.ndarray)  : Image.
        text (str)        : Text string to be drawn.
        org (tuple)       : Bottom-left corner of the text string in the image.
        fontFace (int)    : Font type.
        fontScale (int)   : Font scale factor that is multiplied by the font-specific base size.
        color (str/tuple) : Text color.
        thickness (int)   : Thickness of the lines used to draw a text.
        **kwargs          : ``lineType``, ``bottomLeftOrigin``
            - ``lineType``         : Line type.
            - ``bottomLeftOrigin`` : When true, the image data origin is at the bottom-left corner. Otherwise, it is at the top-left corner.
    
    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.opencv import draw_text_with_bg, cv2read_mpl
        >>> img = cv2read_mpl(filename="path/to/img.png")
        >>> draw_text_with_bg(img=img, offset=(100,-100), text="My name is Shuto")
        >>> plt.imshow(img)
        >>> plt.show()
    """
    if isinstance(color, str):
        color = FAMOUS_COLOR_PALETTES.get(color_type).get(color, COLOR_BLACK)
    if isinstance(bgcolor, str):
        bgcolor = FAMOUS_COLOR_PALETTES.get(color_type).get(bgcolor, COLOR_WHITE)

    (text_W, text_H) = cv2.getTextSize(
        text, fontFace, fontScale=fontScale, thickness=thickness
    )[0]
    text_off_x, text_off_y = offset
    text_off_y += img.shape[0]

    box_coords = (
        (text_off_x, text_off_y), (text_off_x+text_W+2, text_off_y-text_H-2)
    )
    cv2.rectangle(img, *box_coords, bgcolor, cv2.FILLED)
    cv2.putText(
        img, text, (text_off_x, text_off_y), fontFace=fontFace,
        fontScale=fontScale, color=color, thickness=thickness
    )

