#coding: utf-8
import os
import re
import sys
import cv2
import json
import warnings
import argparse
import numpy as np
from tqdm import tqdm
from PIL import Image, ImageFont

from typing import Optional,List,Tuple,Callable

from ..utils._colorings import toBLUE, toGREEN, toACCENT
from ..utils.color_utils import hex2rgb
from ..utils.generic_utils import assign_trbl, now_str, verbose2print, get_random_ttfontname, split_code
from ..utils.argparse_utils import ListParamProcessorCreate
from ..utils.pil_utils import draw_text_in_pil
from ..utils.print_utils import pretty_3quote
from ..utils.monitor_utils import ProgressMonitor

def video_of_typing(argv=sys.argv[1:]):
    """Create a typing video. Before using this program, please do the following things

    - Create a typing json file easily at `JS.35 タイピング風動画を楽に作成する <https://iwasakishuto.github.io/Front-End/tips/JavaScript-35.html>`_
    - Add some keyword arguments for :func:`draw_text_in_pil <pycharmers.utils.pil_utils.draw_text_in_pil>`.

    Args:
        --typing (Tuple[str])   : Path to typing text file(s).
        --typing-fontname (str) : Default Typing Font name
        --size (List[int])      : Output video image size (width, height). Defaults to ``[1080,1920]``.
        --bgRGB (List[int])     : The color of background image. (RGB) Defaults to ``[255,255,255]``. 
        --video (str)           : The path to video to paste. Defaults to ``None``.
        --image (str)           : The path to image to paste. Defaults to ``None``.
        --sec (float)           : The length of the created video. This value is used when ``--video`` is NOT specified. Defaults to ``5``.
        --fps (float)           : The fps of the created video. This value is used when ``--video`` is NOT specified. Defaults to ``30``.
        --margin (int)          : The margin size for pasting video or image. Defaults to ``0``.
        --align (List[str])     : Horizontal and vertical alignment of the content (video/image).
        --out (str)             : The filename of created typing video. Defaults to ``f"typing_video_{now_str()}.mp4"``.
        --quiet (bool)          : Whether to make the output quiet.
    
    Note:
        When you run from the command line, execute as follows::
                
            $ video_of_typing --typing /path/to/typing1.json \\
                                       /path/to/typing2.json \\
                                       /path/to/typing3.json \\
                              --video /path/to/video.mp4 \\
                              --bgRGB "[48,105,152]" \\
                              --align "[center,middle]"
            [Output Typing Video]
            * Frame Count              : 285
            * Frame Length             : 4.8[s]
            * Size (W,H)               : [1080, 1920]
            * Background Color (RGB)   : [48, 105, 152]
            * Output Typing Video Path : typing_video_2021-06-24@23.34.01.mp4
            [Image or Video data to paste]
            * Data              : /path/to/video.mp4
            * Size (W,H)        : (1034, 1590)
            * Margin (top,left) : (165, 23)
            [TypeWriter](/path/tp/typing1.json)
            * ttfontname             : /path/to/851MkPOP_002.ttf
            * fontsize               : 70
            * textRGB                : (0, 0, 0)
            * Number of Typing Texts : 62
            * Move to the next typing every 4.6 from the 0th to the 285th
            [TypeWriter](/path/tp/typing2.json)
            * ttfontname             : /path/to/851MkPOP_002.ttf
            * fontsize               : 100
            * textRGB                : (255, 212, 59)
            * Number of Typing Texts : 1
            * Move to the next typing every 285.0 from the 0th to the 285th
            [TypeWriter](/path/tp/typing3.json)
            * ttfontname             : /path/to/851MkPOP_002.ttf
            * fontsize               : 50
            * textRGB                : (255, 212, 59)
            * Number of Typing Texts : 1
            * Move to the next typing every 285.0 from the 0th to the 285th
            Video of Typing 285/285 [####################]100.00% - 14.107[s]
            Typing Video is saved at typing_video_2021-06-24@23.34.01.mp4

    +----------------------------------------------------------------------------------------------------------------------------------------------------+
    |                                                                     Example                                                                        |
    +=========================================================================+==========================================================================+
    | :class:`BaseTypeWriter <pycharmers.cli.video_of_typing.BaseTypeWriter>` | :class:`CodeTypeWriter <pycharmers.cli.video_of_typing.CodeTypeWriter>`  |
    +-------------------------------------------------------------------------+--------------------------------------------------------------------------+
    |                           |Form-Auto-Fill-In|                           |                        |DNA-Lifetime|                                    |
    +-------------------------------------------------------------------------+--------------------------------------------------------------------------+

    .. |Form-Auto-Fill-In| image:: _images/cli.video_of_typing_text.gif
       :target: https://iwasakishuto.github.io/Form-Auto-Fill-In/UTokyo_Health_Management_Report_Form.html
    .. |DNA-Lifetime| image:: _images/cli.video_of_typing_code.gif
       :target: https://github.com/iwasakishuto/iwasakishuto.github.io/blob/master/.github/workflows/draw-dna-lifetime.yml
    """
    parser = argparse.ArgumentParser(prog="video_of_typing", description="Create a typing Video.", add_help=True)
    parser.add_argument("--typing", type=str, help="Path to typing text file(s).", nargs="*")
    parser.add_argument("--typing-fontname", type=str, help="Default Typing Font name")
    parser.add_argument("--size",   action=ListParamProcessorCreate(type=int), default=[1080,1920], help="The image size. (W,H)")
    parser.add_argument("--bgRGB",  action=ListParamProcessorCreate(type=int), default=[255,255,255], help="The color of background image. (RGB)")
    parser.add_argument("--video",  type=str, default=None, help="The path to input video.")
    parser.add_argument("--sec",    type=float, default=5,  help="The length of the created video. This value is used when 'video' is NOT specified.")
    parser.add_argument("--fps",    type=float, default=None, help="The fps of the created video. This value is used when 'video' is NOT specified.")
    parser.add_argument("--image",  type=str, default=None, help="The path to input image.")
    parser.add_argument("--margin", type=int, default=0, help="The margin size for pasting video or image.")
    parser.add_argument("--align",  action=ListParamProcessorCreate(type=str), default=None, help="horizontal and vertical alignment of the content (video/image).")
    parser.add_argument("--out",    type=str, default=f"typing_video_{now_str()}.mp4", help="The filename of created typing video.")
    parser.add_argument("--quiet",  action="store_true", help="Whether to make the output quiet.")
    args = parser.parse_args(argv)

    video_path = args.video
    image_path = args.image
    out_path = args.out
    bgRGB = args.bgRGB
    bgBGR = bgRGB[::-1]
    align = args.align
    fps = args.fps
    verbose = not args.quiet
    args_kwargs = dict(args._get_kwargs())

    if video_path is not None:
        cap = cv2.VideoCapture(video_path)
        fps = fps or cap.get(cv2.CAP_PROP_FPS)
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    else:
        cap = _VideoCaptureMimic(image_path)
        h,w,_ = cap.frame.shape
        fps = fps or 30
        n = int(args.sec*fps)

    W,H = args.size
    if W < w:
        warnings.warn(f"The output f{toGREEN('width')} is smaller than that of the media, so expand it from {toGREEN(W)} to {toGREEN(w)}.")
        W = w
    if H < h:
        warnings.warn(f"The output f{toGREEN('height')} is smaller than that of the media, so expand it from {toGREEN(H)} to {toGREEN(h)}.")
        H=h
    size = (W,H)

    mt,ml,_,_ = assign_trbl(data=args_kwargs, name="margin")
    if align is not None:
        if "left"   in align: ml = 0
        if "center" in align: ml = (W-w)//2
        if "right"  in align: ml = W-w
        if "top"    in align: mt = 0
        if "middle" in align: mt = (H-h)//2
        if "bottom" in align: mt = H-h

    if verbose:
        print(*pretty_3quote(f"""
        {toACCENT('[Output Typing Video]')}
        * Frame Count              : {toGREEN(n)}
        * Frame Length             : {toGREEN(f"{n/fps:.1f}[s]")}
        * Size (W,H)               : {toGREEN(size)}
        * Background Color (RGB)   : {toGREEN(bgRGB)}
        * Output Typing Video Path : {toBLUE(out_path)} 
        {toACCENT('[Image or Video data to paste]')}
        * Data              : {toBLUE(video_path or image_path)}
        * Size (W,H)        : {toGREEN((w,h))}   
        * Margin (top,left) : {toGREEN((mt,ml))}   
        """))
    
    type_writer = TypeWriter(total_frame_count=n, typing_json_paths=args.typing, verbose=verbose)
    fourcc = cv2.VideoWriter_fourcc(*"H264")
    out_video = cv2.VideoWriter(out_path, fourcc, fps, size)
    monitor = ProgressMonitor(max_iter=n, barname="Video of Typing")
    for i in range(1,n+1):
        bg = np.full(shape=(H,W,3), fill_value=bgBGR, dtype=np.uint8)
        is_ok,frame = cap.read()
        if (not is_ok) or (frame is None): 
            break
        bg[mt:mt+h,ml:ml+w,:] = frame
        bg_img = Image.fromarray(bg)
        bg_img = type_writer.draw_typing_texts(img=bg_img, curt_frame_count=i)
        bg_img = np.asarray(bg_img.convert("RGB"), dtype=np.uint8)
        out_video.write(bg_img)
        monitor.report(it=i)
    monitor.remove()
    cap.release()
    out_video.release()
    if verbose: print(f"Typing Video is saved at {toBLUE(out_path)}")

class _VideoCaptureMimic():
    def __init__(self, image_path:Optional[str]=None):
        if (image_path is None) or (not os.path.isfile(image_path)):
            self.frame = np.zeros(shape=(0,0,3), dtype=np.uint8)
        else:
            self.frame = cv2.imread(image_path)

    def read(self):
        return True,self.frame

    def release(self):
        pass

class BaseTypeWriter():
    def __init__(self, total_frame_count:int, typing_json_paths:Tuple[str]=(), verbose:bool=True):
        """Useful class for drawing typing text.

        Args:
            total_frame_count (int)                  : Total frame count of Typing video.
            typing_json_paths (Tuple[str], optional) : Path to typing text file(s). Defaults to ``()``.
            verbose (bool, optional)                 : Whether to output the typing file information. Defaults to ``True``.
        
        Attributes:
            drawing_functions (List[callable]) : A list of drawing functions for each typing file in ``typing_json_paths``.
        """
        self.print:callable = verbose2print(verbose)
        self.drawing_functions:List[callable] = []
        for path in typing_json_paths:
            drawing_func, messages = self.typing_data_create(json_path=path, total_frame_count=total_frame_count)
            self.print(*messages)
            self.drawing_functions.append(drawing_func)

    @staticmethod
    def typing_data_create(json_path:str, total_frame_count:int, fontsize:int=30, textRGB:Tuple[int,int,int]=(0,0,0), **kwargs) -> Tuple[Callable[[Image.Image, int], Image.Image], List[str]]:
        """Create a drawing function.

        Args:
            json_path (str)                        : Json file which contains typing data. You can easily create this file at `JS.35 タイピング風動画を楽に作成する <https://iwasakishuto.github.io/Front-End/tips/JavaScript-35.html>`_
            total_frame_count (int)                : Total frame count of Typing video.
            fontsize (int, optional)               : Default font size. You can override this value by adding to json file (at ``path``). Defaults to ``30``.
            textRGB (Tuple[int,int,int], optional) : Default font color. You can override this value by adding to json file (at ``path``). Defaults to ``(0,0,0)``.

        Returns:
            Tuple[Callable[[Image.Image, int], Image.Image], List[str]]: Tuple of Drawing function and its settings.
        """
        with open(json_path) as f:
            typing_data = json.load(f)
        _ = typing_data.pop("date", None)
        typing_texts = typing_data.pop("typing", [""])
        num_typing_texts = len(typing_texts)
        s = typing_data.pop("start", 0)
        e = typing_data.pop("end", total_frame_count)
        last = typing_data.pop("last", False)
        span:float = (e-s)/num_typing_texts
        # Keyword Arguments for pycharmers.utils.pil_utils.draw_text_in_pil
        ttfontname = typing_data.pop("ttfontname", None)
        fontsize   = typing_data.pop("fontsize", fontsize)
        textRGB    = tuple(typing_data.pop("textRGB", textRGB))
        textBGR    = textRGB[::-1]
        def draw_typing_text(img, curt_frame_count:int):
            if s<=curt_frame_count:
                if last or curt_frame_count<=e:
                    img,_ = draw_text_in_pil(
                        text=typing_texts[max(min(int((curt_frame_count-s)//span), num_typing_texts-1), 0)],
                        img=img, ttfontname=ttfontname, fontsize=fontsize, textRGB=textBGR,
                        **typing_data
                    )
            return img
        return (draw_typing_text, pretty_3quote(f"""
        {toACCENT('[TypeWriter]')}({toBLUE(json_path)})
        * ttfontname             : {toGREEN(ttfontname)}
        * fontsize               : {toGREEN(fontsize)}
        * textRGB                : {toGREEN(textRGB)}
        * Number of Typing Texts : {toGREEN(num_typing_texts)}
        * Move to the next typing every {toGREEN(f"{span:.1f}")} from the {toGREEN(s)}th to the {toGREEN(e)}th
        """))

    def draw_typing_texts(self, img:Image.Image, curt_frame_count:int) -> Image.Image:
        """Apply each drawing function in ``self.drawing_functions``.

        Args:
            img (Image.Image)      : Input image object.
            curt_frame_count (int) : Current Frame Count

        Returns:
            Image.Image: Image object with typing texts.
        """
        for func in self.drawing_functions:
            img = func(img=img, curt_frame_count=curt_frame_count)
        return img

class CodeTypeWriter(BaseTypeWriter):
    """Useful class for drawing typing programming code"""
    def __init__(self, total_frame_count:int, typing_json_paths:Tuple[str]=(), verbose:bool=True):
        super().__init__(
            total_frame_count=total_frame_count, 
            typing_json_paths=typing_json_paths,
            verbose=verbose,
        )

    @staticmethod
    def typing_data_create(json_path:str, total_frame_count:int, fontsize:int=30, textRGB:Tuple[int,int,int]=(0,0,0), **kwargs) -> Tuple[Callable[[Image.Image, int], Image.Image], List[str]]:
        """Create a drawing function for programming code.

        Args:
            json_path (str)                        : Json file which contains typing data. You can easily create this file at `JS.35 タイピング風動画を楽に作成する <https://iwasakishuto.github.io/Front-End/tips/JavaScript-35.html>`_
            total_frame_count (int)                : Total frame count of Typing video.
            fontsize (int, optional)               : Default font size. You can override this value by adding to json file (at ``path``). Defaults to ``30``.
            textRGB (Tuple[int,int,int], optional) : Default font color. You can override this value by adding to json file (at ``path``). Defaults to ``(0,0,0)``.

        Returns:
            Tuple[Callable[[Image.Image, int], Image.Image], List[str]]: Tuple of Drawing function and its settings.
        """
        with open(json_path) as f:
            typing_data = json.load(f)
        _ = typing_data.pop("date", None)
        typing_texts = typing_data.pop("typing", "")
        num_typing_texts = len(typing_texts)
        s = typing_data.pop("start", 0)
        e = typing_data.pop("end", total_frame_count)
        last = typing_data.pop("last", False)
        span:float = (e-s)/num_typing_texts
        # Keyword Arguments for pycharmers.utils.pil_utils.draw_text_in_pil
        ttfontname = typing_data.pop("ttfontname", get_random_ttfontname())
        fontsize   = typing_data.pop("fontsize", fontsize)
        font = ImageFont.truetype(font=ttfontname, size=fontsize)
        _,fh = font.getsize("hello")
        fontheight = typing_data.pop("fontheight", typing_data.pop("lineheight", fh))
        pygments_theme = typing_data.pop("pygments-theme")
        textRGB = tuple(typing_data.pop("textRGB", textRGB))
        textBGR = textRGB[::-1]
        X = typing_data.pop("X", 0)
        Y = typing_data.pop("Y", 0)
        Xspan = typing_data.pop("Xspan", 0)

        cls2bgr = {}
        with open(pygments_theme) as f:
            for cls,hex in re.findall(
                pattern=r"\.highlight\s+(?:(?:\.((?:\w|-|_)+))?)\s?{.?color:\s*?((?:\w|#)+)", 
                string="".join(f.readlines())):
                rgb = hex2rgb(hex, max_val=255)
                bgr = tuple([int(e) for e in rgb[::-1]])
                cls2bgr[cls] = bgr
            
        def draw_typing_text(img, curt_frame_count:int):
            if s<=curt_frame_count:
                if last or curt_frame_count<=e:
                    x,y = (X,Y)
                    text = typing_texts[:max(min(int((curt_frame_count-s)//span), num_typing_texts), 0)]
                    for code, cls in split_code(text):
                        img,(x,y) = draw_text_in_pil(
                            text=code, img=img, x=x, y=y,
                            ttfontname=ttfontname, fontsize=fontsize, textRGB=cls2bgr.get(cls, textBGR),
                            ret_position="word", **typing_data
                        )
                        x += Xspan
                        if "\n" in code:
                            x = X
                            y += fontheight
            return img
        return (draw_typing_text, pretty_3quote(f"""
        {toACCENT('[Code TypeWriter]')}({toBLUE(json_path)})
        * ttfontname             : {toGREEN(ttfontname)}
        * pygments.css           : {toGREEN(pygments_theme)}
        * fontsize               : {toGREEN(fontsize)}
        * Number of Typing Texts : {toGREEN(num_typing_texts)}
        * Move to the next typing every {toGREEN(f"{span:.1f}")} from the {toGREEN(s)}th to the {toGREEN(e)}th
        """)
        )

class TypeWriter(BaseTypeWriter):
    def __init__(self, total_frame_count:int, typing_json_paths:Tuple[str]=(), verbose:bool=True):
        super().__init__(
            total_frame_count=total_frame_count, 
            typing_json_paths=typing_json_paths,
            verbose=verbose,
        )

    @staticmethod
    def typing_data_create(json_path, **kwargs):
        with open(json_path) as f:
            typing_data = json.load(f)
        if "pygments-theme" in typing_data:
            return CodeTypeWriter.typing_data_create(json_path=json_path, **kwargs)
        else:
            return BaseTypeWriter.typing_data_create(json_path=json_path, **kwargs)