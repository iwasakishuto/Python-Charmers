#coding: utf-8
import os
import re
import sys
import cv2

from ._path import save_dir_create
from .video_image_handler import (basenaming, mono_frame_generator, multi_frame_generator_concat,
                                  count_frame_num, create_VideoWriter)
from .drawing import draw_text_with_bg
from .tracking import tracker_create, BBoxLogger
from ..utils.generic_utils import now_str, flatten_dual, handleKeyError
from ..utils._colorings import toBLUE, toGREEN, toACCENT

DEFAULT_CV_KEYS = {
    "MOVING": {"left": "h", "right": "l", "down": "j", "up": "k"},
    "RATIO" : {"expansion" : "+", "reduction" : "-"},
    "POS"   : {"fullscreen": "f", "topleft": "o"},
    "INFO"  : {"": "i"},
    "QUIT"  : {"1": ("\x1b", "<esc>"), "2": "q"},
    "DELETE": {"": ("\x08", "<delete>")},
    "ENTER" : {"": ("\r", "<enter>")},
    "NUMBER": {str(i):str(i) for i in range(10)},
}
DEFAULT_FRAME_KEYS = DEFAULT_CV_KEYS.copy()
DEFAULT_FRAME_KEYS.update({
    "FRAME" : {"advance": "w", "back": "b", "jump": "@"},
    "RANGE" : {"start": "s", "end": "e"},
    "TAKE"  : {"picture": "p", "video": "v"},
})
DEFAULT_TRACKING_KEYS = DEFAULT_FRAME_KEYS.copy()
DEFAULT_TRACKING_KEYS.update({
    "TRACKING" : {"start": "t", "stop": "c", "init": "n"},
})
DEFAULT_CASCADE_KEYS = DEFAULT_FRAME_KEYS.copy()

class cvKeys():
    """Keys for using openCV

    Examples:
        >>> from pycharmers.opencv import cvKeys, DEFAULT_CV_KEYS
        >>> cvKey = cvKeys(**DEFAULT_CV_KEYS)
        >>> cvKey.QUIT_1_KEY,        cvKey.QUIT_1_KEY_ORD
        ('\x1b', 27)
        >>> cvKey.QUIT_1_KEY_STR,    cvKey.QUIT_1_KEY_STR_ORD
        ('<esc>', -1)
        >>> cvKey.QUIT_KEYS,         cvKey.QUIT_KEYS_ORD
        (['\x1b', 'q'], [27, 113])
        >>> cvKey.QUIT_KEYS_STR,     cvKey.QUIT_KEYS_STR_ORD
        (['<esc>', 'q'], [-1, 113])
        >>> cvKey.HOGE_PIYO_KEY,     cvKey.HOGE_PIYO_KEY_ORD
        (None, -1)
        >>> cvKey.HOGE_PIYO_KEY_STR, cvKey.HOGE_PIYO_KEY_STR_ORD
        (None, -1)
        >>> cvKey.HOGE_KEYS,         cvKey.HOGE_KEYS_ORD
        ([], [])
        >>> cvKey.HOGE_KEYS_STR,     cvKey.HOGE_KEYS_STR_ORD
        ([], [])
        # You can find out all the keys used.
        >>> sorted(cvKey.ALL_KEYS)
    """
    
    def __init__(self, **cv_keys):
        self.group_prefixes = []
        for prefix, keys in cv_keys.items():
            if isinstance(keys, dict):
                self.set_keys(prefix=prefix, **keys)
            else:
                self.__dict__.update({prefix: keys})
    
    @staticmethod
    def ord(c):
        """Return the Unicode code point for a one-character string."""
        return ord(c) if (c is not None) and (len(c)==1) else -1
    
    def __getattr__(self, key):
        if key.endswith("_ORD"):
            key = key[:-4] # key.rstrip("_ORD")
            try:
                val = self.__getattribute__(key)  
            except AttributeError:
                val = self.__getattr__(key)
            return [self.ord(e) for e in val] if isinstance(val, list) else self.ord(val)
        return [] if (key.endswith("KEYS") or key.endswith("KEYS_STR")) else None

            
    def set_keys(self, prefix, **keys):
        prefix = prefix.upper()
        self.group_prefixes.append(prefix)
        
        for key,val in keys.items():
            key = key.upper()
            setattr(self, f"__{prefix}_{key}_KEY",   val)
            setattr(self, f"{prefix}_{key}_KEY",     val[0])
            setattr(self, f"{prefix}_{key}_KEY_STR", val[-1])
                       
        setattr(self.__class__, f"{prefix}_KEYS",     property(lambda self: self.get_group_keys(prefix=prefix, suffix="_KEY")))
        setattr(self.__class__, f"{prefix}_KEYS_STR", property(lambda self: self.get_group_keys(prefix=prefix, suffix="_KEY_STR")))
        
    def get_group_keys(self, prefix="", suffix=""):
        prefix = prefix.upper()
        group_keys = [key for name,key in self.__dict__.items() if re.match(pattern=fr"^{prefix}.+{suffix}$", string=name)]
        return group_keys
    
    @property
    def ALL_KEYS(self):
        return flatten_dual([self.get_group_keys(prefix=prefix, suffix="KEY") for prefix in self.group_prefixes])

def wait_for_input(fmt="Your input : {}", cvKey=cvKeys(**DEFAULT_CV_KEYS)):
    """Wait until the valid input is entered.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv.windows import wait_for_input
        >>> from pycharmers.opencv import SAMPLE_LENA_IMG
        >>> cv2.imshow("lena.png", cv2.imread(SAMPLE_LENA_IMG))
        >>> val = wait_for_input()
        >>> cv2.destroyAllWindows()
    """
    curt_val = ""
    def print_log(curt_val):
        sys.stdout.write("\033[2K\033[G" + fmt.format(curt_val))
        sys.stdout.flush()
    key = cv2.waitKey(0)
    while key not in cvKey.ENTER_KEYS_ORD:
        if key in cvKey.DELETE_KEYS_ORD:
            curt_val = curt_val[:-1]
        else:
            curt_val += chr(key)
        print_log(curt_val)
        key = cv2.waitKey(0)
    print()
    if len(curt_val) == 0:
        curt_val = wait_for_input()
    return curt_val

def wait_for_choice(*keys):
    """Wait until choicing the one of the keys.

    Args:
        *keys: Keys.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv.windows import wait_for_choice
        >>> from pycharmers.opencv import cv2plot, SAMPLE_LENA_IMG
        >>> cv2.imshow("lena.png", cv2.imread(SAMPLE_LENA_IMG))
        >>> val = wait_for_choice(*list("ltrb"))
        >>> cv2.destroyAllWindows()
    """
    num_choices = len(keys)
    max_len = len(max(keys, key=len))
    int2key = dict(zip(range(num_choices), keys))

    print("\nPlease input the corresponding number.")
    for i,k in int2key.items():
        print(f" - {k:<{max_len}}: {i}")

    while True:
        i = int(wait_for_input())
        if 0 <= i < num_choices:
            break
        else:
            print(f"* Please input from 0 to {num_choices-1} (got {i})")
    return keys[i]

class cvWindow():
    """Window & Image Location

    - ``Ix,Iy,Iw,Ih = cv2.getWindowImageRect(winname)``
    - ``cv2.moveWindow(winname, Wx, Wy)``

    Variable Names::

        (Wx,Wy) ----------------------- (x+w,y)
            |               ^                |
            |               | Fh             |
            |               v                |
            |     (Ix,Iy) ------ (Ix+w,Iy)   |
            |   Fw   |               |       |
            |<------>|     Image     |       |
            |        |               |       |
            |    (Ix,Iy+h) ---- (Ix+w,Iy+h)  |
            |                                |
        (Wx,Wy+h) --------------------- (Wx+w,Wy+h)

    Args:
        no (int) : The number of windows.

    Attributes:
        video_save_dir (str)   : ``Path/to/created_video/directory``
        img_save_dir (str)     : ``Path/to/created_image/directory``
        reduction_rate (float) :  ``1./expansion_rate``
        cvKey (cvKeys)         : Keys that can be used with OpenCV.
        iIh, iIw (int)         : 
    """
    no = 0

    def __init__(self, winname=None, dirname=None, move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_CV_KEYS)):
        """initialization of the OpenCV Windows.

        Args:
            winname (str)          : The window name.
            dirname (str)          : dirname for saved image or directory.
            move_distance (int)    : Moving distance. (px)
            expansion_rate (float) : Expansion Rate.
            cv_keys (dict)         : ``<pycharmers.opencv.windows.cvKeys object>``.

        Examples:
            >>> from pycharmers.opencv import cvWindow
            >>> window = cvWindow()
        """
        self.setup(winname=winname, dirname=dirname)

        self.move_distance = move_distance
        self.expansion_rate = expansion_rate
        self.cvKey = cvKey

        self.iIh = None
        self.iIw = None

    @property
    def reduction_rate(self):
        return 1./self.expansion_rate

    def setup(self, winname=None, dirname=None):
        """Setting up for the OpenCV windows.

        - Decide window name.
        - Decide and Create the location of the directory to save image.

        Args:
            winname (str) : Unique winname.
            dirname (str) : dirname for saved image or directory.
        """
        # Decide window name.
        cvWindow.no += 1
        if winname is None:
            winname = f"frame {cvWindow.no:>02}"
        self.winname = winname
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)
        # Decide the location of the directory to save image.
        self.img_save_dir, self.video_save_dir = save_dir_create(dirname=dirname, image=True, video=True, json=False)

    @property
    def frame_size(self):
        """Get Frame width (``Fw``) and Frame height (``Fh``)"""
        _,_,Fw,Fh = self.get_anchors()
        return (Fw,Fh)

    @property
    def image_size(self):
        """Get Image width (``Iw``) and Image height (``Ih``)"""
        _,_,Iw,Ih = self.getWindowImageRect()
        return (Iw,Ih)

    def resizeWindow(self, width, height):
        """Resizes window to the specified size

        Args:
            width (int)  : The new window width.
            height (int) : The new window height.
        """
        cv2.resizeWindow(winname=self.winname, width=width, height=height)

    def moveWindow(self, x, y):
        """Moves window to the specified position

        Args:
            x (int): The new x-coordinate of the window.
            y (int): The new y-coordinate of the window.
        """
        cv2.moveWindow(winname=self.winname, x=x, y=y)

    def getWindowImageRect(self):
        """Provides rectangle of image in the window.

        The function getWindowImageRect returns the client screen coordinates, width and height of the image rendering area.
        """
        Ix,Iy,Iw,Ih = cv2.getWindowImageRect(winname=self.winname)
        return (Ix,Iy,Iw,Ih)

    def getWindowRect(self):
        """Get window bounding boxes as ``(x,y,w,h)``"""
        Wx,Wy,Fw,Fh = self.get_anchors()
        Iw,Ih = self.image_size
        Ww = Iw+Fw*2; Wh = Ih+Fh*2
        return (Wx,Wy,Ww,Wh)

    def get_anchors(self):
        """ Get the ``(Wx,Wy,Fw,Fh)`` 
        
        Notes:
            - ``self.getWindowImageRect()`` gets the rectangle of image in the window.
            - ``self.moveWindow(x, y)`` make the window left top to ``(x,y)``
        
        """
        Ix,Iy,_,_ = self.getWindowImageRect()
        self.moveWindow(Ix, Iy)
        # NOTE: Get the (Ix+Fw,Iy+Fw) in the initial window.
        Ix_Fw,Iy_Fw,_,_ = self.getWindowImageRect()
        Fw = Ix_Fw-Ix; Fh = Iy_Fw-Iy
        Wx = Ix-Fw;    Wy = Iy-Fh
        # Reset the window position.
        self.moveWindow(Wx, Wy)
        return (Wx,Wy,Fw,Fh)

    def show(self, mat):
        """Displays an image in the specified window. (``self.winname``)
        
        Args:
            mat (np.ndarray): Image to be shown.
        """
        if self.iIh is None or (self.iIh, self.iIw) != mat.shape[:2]:
            self.iIh, self.iIw, _ = mat.shape
            self.Ih,  self.Iw,  _ = mat.shape
            self.resizeWindow(height=self.iIh, width=self.iIw)
        cv2.imshow(winname=self.winname, mat=mat)

    def _ret_info(self):
        """ Return Key Information. """
        cvKey = self.cvKey
        return f"""
        {toACCENT(f'[Window Name {self.winname}]')}
        # Move window : {toBLUE(str(self.move_distance) + 'px')}
        - To move {toBLUE('left')+',':<15} press {toGREEN(cvKey.MOVING_LEFT_KEY_STR)}
        - To move {toBLUE('right')+',':<15} press {toGREEN(cvKey.MOVING_RIGHT_KEY_STR)}
        - To move {toBLUE('down')+',':<15} press {toGREEN(cvKey.MOVING_DOWN_KEY_STR)}
        - To move {toBLUE('up')+',':<15} press {toGREEN(cvKey.MOVING_UP_KEY_STR)}
        # window position
        - To align {toBLUE('top & left')}, press {toGREEN(cvKey.POS_TOPLEFT_KEY_STR)}
        - To make the window {toBLUE('fullscreen')}, press {toGREEN(cvKey.POS_FULLSCREEN_KEY_STR)}
        # Expansion & Reduction : {toBLUE(f'{self.expansion_rate:.1%}')}
        - To {toBLUE('expand')} window, press {toGREEN(cvKey.RATIO_EXPANSION_KEY_STR)}
        - To {toBLUE('shrink')} window, press {toGREEN(cvKey.RATIO_REDUCTION_KEY_STR)}
        # Quit
        - To {toBLUE('quit')}, press {', '.join([toGREEN(e) for e in cvKey.QUIT_KEYS_STR])}
        # Info
        - To get the window rectangle, press {toGREEN(cvKey.INFO__KEY_STR)}
        """

    def describe(self):
        """Describe Key info."""
        print(self._ret_info())

    def recieveKey(self, key):
        """Response according to Recieved key.

        Args:
            key (int): Input Key. (= ``cv2.waitKey(0)``)

        Returns:
            is_break (bool) Whether loop break or not. If break, destroy the window.
        """
        is_break = False
        cvKey = self.cvKey
        winname = self.winname

        if key in cvKey.QUIT_KEYS_ORD:
            cv2.destroyWindow(winname)
            is_break = True

        elif key in cvKey.MOVING_KEYS_ORD:
            Wx,Wy,_,_ = self.get_anchors()

            if key == cvKey.MOVING_LEFT_KEY_ORD:
                Wx-=self.move_distance
            elif key == cvKey.MOVING_RIGHT_KEY_ORD:
                Wx+=self.move_distance
            elif key == cvKey.MOVING_DOWN_KEY_ORD:
                Wy+=self.move_distance
            else: # key == cvKey.MOVING_UP_KEY_ORD
                Wy-=self.move_distance

            self.moveWindow(Wx, Wy)

        elif key in cvKey.RATIO_KEYS_ORD:
            if key == cvKey.RATIO_EXPANSION_KEY_ORD:
                rate = self.expansion_rate
            else:
                rate = self.reduction_rate

            self.Ih = int(rate*self.Ih)
            self.Iw = int(rate*self.Iw)
            self.resizeWindow(width=self.Iw, height=self.Ih)

        elif key in cvKey.INFO_KEYS_ORD:
            print(f"Window Rectangle: {self.getWindowRect()}")

        elif key in cvKey.POS_KEYS_ORD:
            if key == cvKey.POS_FULLSCREEN_KEY_ORD:
                """
                ``cv2.WINDOW_NORMAL = 0``
                ``cv2.WINDOW_FULLSCREEN = 1``
                """
                cv2.setWindowProperty(
                    winname=winname,
                    prop_id=cv2.WND_PROP_FULLSCREEN,
                    prop_value=1-cv2.getWindowProperty(
                        winname=winname,
                        prop_id=cv2.WND_PROP_FULLSCREEN,
                    )
                )
            else:
                self.moveWindow(0, 0)

        return is_break

class FrameWindow(cvWindow):
    """OpenCV window for Frames (images or video).

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import FrameWindow, SAMPLE_VTEST_VIDEO
        >>> window = FrameWindow(SAMPLE_VTEST_VIDEO)
        >>> # window.describe()
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    def __init__(self, *input_path, winname=None, dirname=None, move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_FRAME_KEYS)):
        self.basenames = ".".join([basenaming(path) for path in input_path])
        super().__init__(
            winname=winname,
            dirname=dirname,
            move_distance=move_distance,
            expansion_rate=expansion_rate,
            cvKey=cvKey,
        )
        self.input_path_ = input_path[0]
        self.input_path  = input_path
        self.frame_generator = {
            True  : mono_frame_generator,
            False : multi_frame_generator_concat,
        }[len(input_path)==0]
        self.gen = self.frame_generator(*input_path)
        self.total_num = count_frame_num(input_path[0])
        self.frame_num = 1
        self.start_ = self.end_ = None
        self.show(self.gen.__next__())

    def show(self, mat):
        """Displays an image in the specified window. (``self.winname``)
        
        Args:
            mat (np.ndarray): Image to be shown.
        """
        draw_text_with_bg(
            img=mat, text=f"{self.frame_num}/{self.total_num}",
            org=(50, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=3, color=(0,0,0), bgcolor=(255,255,255),
            color_type="css4", thickness=1,
        )
        super().show(mat)

    def recieveKey(self, key):
        """Response according to Recieved key.

        Args:
            key (int): Input Key. (= ``cv2.waitKey(0)``)

        Returns:
            is_break (bool) Whether loop break or not. If break, destroy the window.
        """
        is_break = False
        cvKey = self.cvKey
        
        if key in cvKey.FRAME_KEYS_ORD:
            if key == cvKey.FRAME_ADVANCE_KEY_ORD:
                self.frame_num = min(self.total_num, self.frame_num+1)
            elif key == cvKey.FRAME_BACK_KEY_ORD:
                self.frame_num = max(1, self.frame_num-1)
            elif key == cvKey.FRAME_JUMP_KEY_ORD:
                frame_num = int(wait_for_input(fmt="Jump to {} frame."))
                self.frame_num = max(1, min(int(frame_num), self.total_num))
            self.gen = self.frame_generator(*self.input_path, frame_num=self.frame_num-1)
            self.show(self.gen.__next__())
        elif key in cvKey.RANGE_KEYS_ORD:
            pos = "start" if key == cvKey.RANGE_START_KEY_ORD else "end"
            self.__dict__[pos+"_"] = self.frame_num
            print(f"{pos}: {self.frame_num} frame.")
            if (self.start_ is not None) and (self.end_ is not None):
                self.range_processing()
        elif key == cvKey.TAKE_PICTURE_KEY_ORD:
            self.gen = self.frame_generator(*self.input_path, frame_num=self.frame_num-1)
            frame = self.gen.__next__()
            fn = f"{self.basenames}({self.frame_num}-out-of-{self.total_num}).png"
            cv2.imwrite(os.path.join(self.img_save_dir, fn), frame)
            print(f"Take a screenshot ({self.frame_num} frame)")
        else:
            is_break = super().recieveKey(key)
        return is_break

    def range_processing(self):
        """Select a range and process the image or video of that part."""
        start = self.start_
        end = self.end_
        span = end-start+1
        if span<0:
            print("`start` must be an earlier frame than `end`.")
        else:
            cvKey = self.cvKey
            print(f"""
            # You select {start}-{end} frame
            - press '{toBLUE(cvKey.TAKE_VIDEO_KEY_STR)}' to extract a video.
            - press '{toBLUE(cvKey.TAKE_PICTURE_KEY_STR)}' to shot all frames in the range.
            """)
            gen = self.frame_generator(*self.input_path, frame_num=start-1)
            total_num = self.total_num
            while True:
                key = cv2.waitKey(0)
                handleKeyError(lst=cvKey.TAKE_KEYS, key=chr(key))
                if key == cvKey.TAKE_PICTURE_KEY_ORD:
                    for i,frame in enumerate(gen):
                        current = start+i
                        fn = f"{self.basenames}.{current}.out.of.{total_num}.png"
                        cv2.imwrite(os.path.join(self.img_save_dir, fn), frame)
                        if current >= end: break
                    print(f"Take a screenshots from {start} frame to {end} frame.")
                    break
                elif key == cvKey.TAKE_VIDEO_KEY_ORD:
                    video_fn = f"{self.basenames}.{start}.to.{end}.out.of.{total_num}.mp4"
                    out_video = create_VideoWriter(
                        in_path=self.input_path_,
                        out_path=os.path.join(self.video_save_dir, video_fn)
                    )
                    for i,frame in enumerate(gen):
                        out_video.write(frame)
                        if start+i >= end: break
                    out_video.release()
                    print(f"Extract a video from {start} frame to {end} frame.")
                    break
        self.start_ = self.end_ = None

    def _ret_info(self):
        """ Return Key Information. """
        cvKey = self.cvKey
        info  = super()._ret_info()
        info += f"""\
        # Frame Control
        - To {toGREEN('advance')+' frame,':<23} press '{toBLUE(cvKey.FRAME_ADVANCE_KEY_STR)}'
        - To {toGREEN('back')+' frame,':<23} press '{toBLUE(cvKey.FRAME_BACK_KEY_STR)}'
        - To {toGREEN('jump to')+' frame,':<23} press '{toBLUE(cvKey.FRAME_JUMP_KEY_STR)}'
        \tThen,
        \t- To {toGREEN('specify')} the frame, press '{toBLUE('<number_key>')}'
        \t- To {toGREEN('delete')} character,  press '{toBLUE(cvKey.DELETE__KEY_STR)}'
        \t- To {toGREEN('finish')} the entry,  press '{toBLUE(cvKey.ENTER__KEY_STR)}'
        # Video Editing
        - To {toGREEN('take a screenshot')}, press '{toBLUE(cvKey.TAKE_PICTURE_KEY_STR)}' .
        - When you deal with a contiguous range of video,
        \t- press '{toBLUE(cvKey.RANGE_START_KEY_STR)}', and '{toBLUE(cvKey.RANGE_END_KEY_STR)}' to select the range.
        \t- press '{toBLUE(cvKey.TAKE_VIDEO_KEY_STR)}' to {toGREEN('extract a video')}.
        \t- press '{toBLUE(cvKey.TAKE_PICTURE_KEY_STR)}' to {toGREEN('shot all frames')} in the range.
        """
        return info

class TrackingWindow(FrameWindow):
    """OpenCV window for Trackings (images or video).

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import TrackingWindow, SAMPLE_VTEST_VIDEO
        >>> window = TrackingWindow(path=SAMPLE_VTEST_VIDEO, tracker="boosting", coord_type="xywh")
        >>> # window.describe()
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    def __init__(self, path, tracker="boosting", coord_type="xywh", bbox=(0,0,0,0),
                 winname=None, dirname=None, move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_TRACKING_KEYS), **metadata):
        super().__init__(
            path,
            winname=winname,
            dirname=dirname,
            move_distance=move_distance,
            expansion_rate=expansion_rate,
            cvKey=cvKey,
        )
        self.moveWindow(0, 0)
        # Preparation for Tracking
        self.draw_bboxes = draw_bboxes_create(coord_type=coord_type)
        self.tracker = tracker_create(tracker)
        self.logger = None
        self.bbox = self.init(bbox=bbox, coord_type=coord_type, input_path=path, dirname=dirname, tracking_method=str(tracker)) 

    @property
    def init_bbox_winname(self):
        return self.winname + "-initial_bbox"

    def init(self, bbox=(0,0,0,0), coord_type="xywh", input_path=None, dirname=None, **metadata):
        if self.logger is not None: 
            self.logger.save()
        self.logger = BBoxLogger(coord_type=coord_type, input_path=input_path, dirname=dirname, **metadata)

        # Get curt (initial) frame.
        frame = self.gen.__next__()
        self.gen = self.frame_generator(*self.input_path, frame_num=self.frame_num)
        if min((bbox[-2:])) == 0:
            bbox = cv2.selectROI(windowName=self.init_bbox_winname, img=frame, showCrosshair=True, fromCenter=False)
        else:
            frame = self.draw_bboxes(frame=frame, bboxes=bbox, info={"text": "initial"})  
            cv2.imshow(self.init_bbox_winname, frame)
        self.tracker.init(frame, bbox) 
        self.logger.add_bboxes(no=self.frame_num, bboxes=bbox)
        return bbox

    def recieveKey(self, key):
        """Response according to Recieved key.

        Args:
            key (int): Input Key. (= ``cv2.waitKey(0)``)

        Returns:
            is_break (bool) Whether loop break or not. If break, destroy the window.
        """
        is_break = False
        cvKey = self.cvKey
        
        if key in cvKey.TRACKING_KEYS_ORD:
            if key==cvKey.TRACKING_INIT_KEY_ORD:
                self.gen = self.frame_generator(*self.input_path, frame_num=self.frame_num-1)
                frame = self.gen.__next__()
                self.bbox = cv2.selectROI(windowName=self.winname + "_initial_bbox", img=frame, showCrosshair=True, fromCenter=False)
                self.tracker.init(frame, self.bbox) 
            else:
                for frame in self.gen:
                    self.frame_num += 1
                    track, bbox = self.tracker.update(frame)
                    self.logger.add_bboxes(no=self.frame_num, bboxes=bbox)
                    if track:
                        bbox = [int(e) for e in bbox]
                        frame = self.draw_bboxes(frame=frame, bboxes=bbox)
                    else:
                        draw_text_with_bg(
                            img=frame, text="failure", org=(50,50),
                            fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=3,
                            color="red", bgcolor="white", color_type="css4",
                            thickness=1,
                        )
                    self.show(frame)
                    k = cv2.waitKey(1)
                    if k==cvKey.TRACKING_STOP_KEY_ORD: break
        else:
            is_break = super().recieveKey(key)
        return is_break


    def _ret_info(self):
        """ Return Key Information. """
        cvKey = self.cvKey
        info  = super()._ret_info()
        info += f"""\
        # Tracking
        - To {toGREEN('start')+' tracking,':<25} press '{toBLUE(cvKey.TRACKING_START_KEY_STR)}'
        - To {toGREEN('stop')+' tracking,':<25} press '{toBLUE(cvKey.TRACKING_STOP_KEY_STR)}'
        - To {toGREEN('initialize')+' bbox,':<25} press '{toBLUE(cvKey.TRACKING_INIT_KEY_STR)}'
        """
        return info