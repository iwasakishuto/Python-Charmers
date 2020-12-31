"""Define functions and classes to make OpenCV window easier to use. """
#coding: utf-8
import os
import re
import sys
import cv2
from tabulate import tabulate

from ._path import save_dir_create
from .video_image_handler import (basenaming, mono_frame_generator, multi_frame_generator_concat,
                                  count_frame_num, create_VideoWriter)
from .drawing import draw_text_with_bg, draw_bboxes_create
from .tracking import tracker_create, BBoxLogger
from ..utils.generic_utils import now_str, flatten_dual, handleKeyError
from ..utils._colorings import toRED, toBLUE, toGREEN, toACCENT

DEFAULT_CV_KEYS = {
    "BASE": ["To send the window the command '{name}'", {
        "info": "i",
        "quit": "q",
        "delete": "<delete>",
        "enter": "<enter>",
    }],
    "MOVING" : ["To move the window to the '{name}'", {
        "left": "h", 
        "right": "l",
        "down": "j", 
        "up": "k",
    }],
    "RATIO" : ["To '{name}' the window", {
        "expansion" : "+", 
        "reduction" : "-",
    }],
    "POSITION" : ["To set/know the window '{name}'", {
        "fullscreen": "f", 
        "topleft": "o",
        "rectangle": "r",
    }],
}
DEFAULT_FRAME_KEYS = {
    "FRAME" : ["", {
        "advance": "w", 
        "back": "b", 
        "jump": "@"
    }],
    "RANGE" : ["", {
        "start": "s",
        "end": "e"
    }],
    "TAKE"  : ["",{
        "picture": "p", 
        "video": "v"
    }],
}
DEFAULT_TRACKING_KEYS = {
    "TRACKING" : ["", {
        "start": "t", 
        "stop": "c", 
        "init": "n"
    }],
}

class cvKeys():
    """Keys for using openCV

    Args:
        cv_keys (dict) : Key information. See :meth:`set_keys <pycharmers.opencv.windows.cvKeys.set_keys>` . ``{group: [fmt, {name1:key1, name2:key2,...}]}``

    Attributes:
        info_table (list)         : List-style Information. This strings are used in method :meth:`describe <pycharmers.opencv.windows.cvKeys.describe>`
        groups (list)             : Group list.
        GROUP_NAME_KEY (str)      : Key for a command.
        GROUP_NAME_KEY_ORD (int)  : Ord of the Key ( ``GROUP_NAME_KEY`` )
        GROUP_KEYS (list)         : Keys for a group commands.
        GROUP_KEYS_ORD (list)     : Ords of the all Keys in a group ( ``GROUP_KEYS`` )
        ALL_KEYS (list)           : All Keys for commands.
        ALL_KEYS_ORD (list)       : All ords of the all Keys (``ALL_KEYS``)

    Examples:
        >>> from pycharmers.opencv import cvKeys, DEFAULT_CV_KEYS
        >>> cvKey = cvKeys(**DEFAULT_CV_KEYS)
        >>> cvKey.MOVING_LEFT_KEY
        'h'
        >>> cvKey.MOVING_LEFT_KEY_ORD
        104
        >>> cvKey.MOVING_KEYS
        ['h', 'l', 'j', 'k']
        >>> cvKey.MOVING_KEYS_ORD
        [104, 108, 106, 107]
        >>> cvKey.ALL_KEYS
        ['i', 'q', '<delete>', '<enter>', 'h', 'l', 'j', 'k', '+', '-', 'f', 'o']
        >>> cvKey.ALL_KEYS_ORD
        [105, 113, 8, 13, 104, 108, 106, 107, 43, 45, 102, 111]

    """    
    def __init__(self, **cv_keys):
        self.groups = []; self.info_table = []
        for group,(fmt,keys) in cv_keys.items():
            self.set_keys(group=group, fmt=fmt, **keys)

    def __getattr__(self, name):
        """When suffix of attribute is 

        * XXX_KEYS_ORD, return the Unicode code points for XXX_KEYS. (list)
        * XXX_KEY_ORD, return the Unicode code point for XXX_KEY. (int)
        """
        ord_match = re.match(pattern=r"^(.+_KEYS?)_ORD$", string=name)
        if ord_match:
            key_str = self.__getattribute__(ord_match.group(1))
            if isinstance(key_str, list):
                return [self.ord(key) for key in key_str]
            else: # isinstance(key, str)
                return self.ord(key_str)

    def set_keys(self, group, fmt, **keys):
        """Set keys.

        Args:
            group (str) : A group name. (ex. ``"MOVING"`` )
            fmt (str)   : How to describe group keys. Need to contain "{name}" (ex. ``"To move the window to the {name}"`` )
            keys (dict) : {name1:key1, name2:key2,...}
                        * name (str)  : A name in the ``group`` . (ex. ``"left"`` )
                        * key (str)   : A key corresponding to the ``name`` . (ex. ``"l"``)
        """
        group = group.upper()
        self.groups.append(group)
        self.info_table.append([toRED(group), "", ""])
        for name, key in keys.items():
            self.info_table.append(["", fmt.format(name=toGREEN(name)), f"press {toBLUE(key)}"])
            setattr(self, f"{group}_{name.upper()}_KEY", key)
        setattr(self.__class__, f"{group}_KEYS", property(fget=lambda self: self._get_group_keys(group=group)))

    @property
    def info(self):
        return tabulate(self.info_table, headers=["group", f"description ('{toGREEN('name')}')", "key"], tablefmt="grid")

    def describe(self):
        """Describe Key information."""
        print(self.info)

    def _get_group_keys(self, group=""):
        return [key for name,key in self.__dict__.items() if re.match(pattern=fr"^{group.upper()}.+$", string=name)]

    @staticmethod
    def ord(c=None):
        """Return the Unicode code point for a one-character string.
        
        Args:
            c (str) : A character

        Return:
            i (int) : Unicode code point

        Examples:
            >>> from pycharmers.opencv import cvKeys
            >>> cvKey = cvKeys()
            >>> cvKey.ord("l") == ord("l")
            True
            >>> cvKey.ord("<delete>")
            8
            >>> ord("<delete>")
            TypeError: ord() expected a character, but string of length 8 found
        """
        c = re.sub(pattern=r"<(.+)>",repl=lambda m:{"delete":"\x08","enter":"\r"}[m.group(1)], string=str(c))
        return ord(c) if len(c)==1 else -1
    
    @property
    def ALL_KEYS(self):
        """Return all the keys that have been set."""
        return flatten_dual([self._get_group_keys(group=group) for group in self.groups])

def wait_for_input(fmt="Your input : {val}", cvKey=cvKeys(**DEFAULT_CV_KEYS)):
    """Wait until the valid input is entered.

    Args:
        fmt (str)      : Format to show your current input value. ( ``"{val}"`` must be included.)
        cvKey (cvKeys) : Instance of :class:`cvKeys <pycharmers.opencv.windows.cvKeys>`

    Returns:
        curt_val (str) : Input string.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import wait_for_input, SAMPLE_LENA_IMG
        >>> cv2.imshow("lena.png", cv2.imread(SAMPLE_LENA_IMG))
        >>> val = wait_for_input()
        >>> cv2.destroyAllWindows()
    """
    def print_log(curt_val):
        sys.stdout.write("\033[2K\033[G" + fmt.format(val=curt_val))
        sys.stdout.flush()

    curt_val = ""; print_log(curt_val)
    while True:
        key = cv2.waitKey(0)
        if key == cvKey.BASE_ENTER_KEY_ORD:
            break
        elif key == cvKey.BASE_DELETE_KEY_ORD:
            curt_val = curt_val[:-1]
        else:
            curt_val += chr(key)
        print_log(curt_val)    
    print()
    if len(curt_val) == 0:
        # Process recursively
        curt_val = wait_for_input()
    return curt_val

def wait_for_choice(*choices):
    """Wait until choicing the one of the keys.

    Args:
        choices (tuple): Choices.

    Returns:
        choice (element) : The ith element in ``choices`` . ( ``i`` means Your input. )

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import wait_for_choice, SAMPLE_LENA_IMG
        >>> cv2.imshow("lena.png", cv2.imread(SAMPLE_LENA_IMG))
        >>> val = wait_for_choice(*list("ltrb"))
        >>> cv2.destroyAllWindows()
    """
    max_val = len(choices)-1
    print(tabulate([[i,c] for i,c in enumerate(choices)], headers=["Input", "Choice"], tablefmt="pretty"))
    while True:
        i = int(wait_for_input())
        if 0 <= i <= max_val:
            break
        else:
            print(f"[ERROR] Please input from 0 to {max_val} (got {i})")
    return choices[i]

class cvWindow():
    """Window & Image Location

    - Ix,Iy,Iw,Ih = :meth:`getWindowImageRect <pycharmers.opencv.windows.cvWindow.getWindowImageRect>`
    - :meth:`moveWindow <pycharmers.opencv.windows.cvWindow.moveWindow>` make the window left top to ``(x,y)``

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

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import cvWindow
        >>> window = cvWindow()
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    no = 0

    def __init__(self, winname=None, dirname=None, move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_CV_KEYS)):
        """initialization of the OpenCV Windows.

        Args:
            winname (str)          : The window name.
            dirname (str)          : dirname for saved image or directory.
            move_distance (int)    : Moving distance. (px)
            expansion_rate (float) : Expansion Rate.
            cvKey (dict)           : Instance of :class:`cvKeys <pycharmers.opencv.windows.cvKeys>`.
        """
        self.setup(winname=winname, dirname=dirname)
        self.move_distance = move_distance
        self.expansion_rate = expansion_rate
        self.cvKey = cvKey
        self.describe()

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
        self.Iw, self.Ih = self.image_size

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
            - :meth:`getWindowImageRect <pycharmers.opencv.windows.cvWindow.getWindowImageRect>` gets the rectangle of image in the window.
            - :meth:`moveWindow <pycharmers.opencv.windows.cvWindow.moveWindow>` make the window left top to ``(x,y)``
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
        if (self.Ih, self.Iw) != mat.shape[:2]:
            self.Ih, self.Iw,  _ = mat.shape
            self.resizeWindow(height=self.Ih, width=self.Iw)
        cv2.imshow(winname=self.winname, mat=mat)

    def _ret_info(self):
        """ Return Key Information. """
        return self.cvKey.info

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

        # Quit.
        if key == cvKey.BASE_KEYS_ORD:
            if key == cvKey.BASE_QUIT_KEY_ORD:
                cv2.destroyWindow(winname)
                is_break = True
            elif key == cvKey.BASE_INFO_KEY_ORD:
                self.describe()

        # MOVING
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

        # RATIO
        elif key in cvKey.RATIO_KEYS_ORD:
            if key == cvKey.RATIO_EXPANSION_KEY_ORD:
                rate = self.expansion_rate
            else:
                rate = self.reduction_rate

            self.Ih = int(rate*self.Ih)
            self.Iw = int(rate*self.Iw)
            self.resizeWindow(width=self.Iw, height=self.Ih)

        elif key in cvKey.POSITION_KEYS_ORD:
            if key == cvKey.POSITION_FULLSCREEN_KEY_ORD:
                """
                - ``cv2.WINDOW_NORMAL`` = ``0``
                - ``cv2.WINDOW_FULLSCREEN = ``1``
                """
                cv2.setWindowProperty(
                    winname=winname,
                    prop_id=cv2.WND_PROP_FULLSCREEN,
                    prop_value=1-cv2.getWindowProperty(
                        winname=winname,
                        prop_id=cv2.WND_PROP_FULLSCREEN,
                    )
                )
            elif key == cvKey.POSITION_TOPLEFT_KEY_ORD:
                self.moveWindow(0, 0)
            elif key == cvKey.POSITION_RECTANGLE_KEY_ORD:
                print(f"Window Rectangle: {self.getWindowRect()}")

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

# __doc__ += "\n"+cvKeys(**DEFAULT_CV_KEYS).info