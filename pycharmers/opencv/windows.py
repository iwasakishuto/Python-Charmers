"""Define functions and classes to make OpenCV window easier to use. 

This KEY table is created by the following programs.

.. code-block:: python

    >>> from pycharmers.utils import tabulate
    >>> from pycharmers.opencv import *
    >>> lst = []
    >>> for DEFAULT_KEY_NAME in list(filter(lambda x:x.startswith("DEFAULT_") and x.endswith("_KEYS"), globals().keys())):
    >>>     for group,(fmt,keys) in eval(DEFAULT_KEY_NAME).items():
    >>>         for name, key in keys.items():
    >>>             lst.append([DEFAULT_KEY_NAME, group, fmt.format(name=name), f"'{key}'"])
    >>>             DEFAULT_KEY_NAME, group = ("", "")
    >>> tabulate(lst, headers=["VARNAME", "group", "description ('name')", "key"], tablefmt="grid")

+-----------------------+----------+-----------------------------------------+------------+
|        VARNAME        |  group   |          description ('name')           |    key     |
+=======================+==========+=========================================+============+
|       DEFAULT_CV_KEYS |     BASE |   To send the window the command 'info' |        'i' |
+                       +          +-----------------------------------------+------------+
|                       |          |   To send the window the command 'quit' |        'q' |
+                       +          +-----------------------------------------+------------+
|                       |          | To send the window the command 'delete' | '<delete>' |
+                       +          +-----------------------------------------+------------+
|                       |          |  To send the window the command 'enter' |  '<enter>' |
+                       +----------+-----------------------------------------+------------+
|                       |   MOVING |        To move the window to the 'left' |        'h' |
+                       +          +-----------------------------------------+------------+
|                       |          |       To move the window to the 'right' |        'l' |
+                       +          +-----------------------------------------+------------+
|                       |          |        To move the window to the 'down' |        'j' |
+                       +          +-----------------------------------------+------------+
|                       |          |          To move the window to the 'up' |        'k' |
+                       +----------+-----------------------------------------+------------+
|                       |    RATIO |               To 'expansion' the window |        '+' |
+                       +          +-----------------------------------------+------------+
|                       |          |               To 'reduction' the window |        '-' |
+                       +----------+-----------------------------------------+------------+
|                       | POSITION |     To set/know the window 'fullscreen' |        'f' |
+                       +          +-----------------------------------------+------------+
|                       |          |        To set/know the window 'topleft' |        'o' |
+                       +          +-----------------------------------------+------------+
|                       |          |      To set/know the window 'rectangle' |        'r' |
+-----------------------+----------+-----------------------------------------+------------+
|    DEFAULT_FRAME_KEYS |    FRAME |                      To 'advance' frame |        'w' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To 'back' frame |        'b' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To 'jump' frame |        '@' |
+                       +----------+-----------------------------------------+------------+
|                       |    RANGE |                 To select range 'start' |        's' |
+                       +          +-----------------------------------------+------------+
|                       |          |                   To select range 'end' |        'e' |
+                       +----------+-----------------------------------------+------------+
|                       |     TAKE |                       To take 'picture' |        'p' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To take 'video' |        'v' |
+-----------------------+----------+-----------------------------------------+------------+
| DEFAULT_REALTIME_KEYS |     TAKE |                       To take 'picture' |        'p' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To take 'video' |        'v' |
+-----------------------+----------+-----------------------------------------+------------+
| DEFAULT_TRACKING_KEYS | TRACKING |                        To track 'start' |        't' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To track 'stop' |        'c' |
+                       +          +-----------------------------------------+------------+
|                       |          |                         To track 'init' |        'n' |
+-----------------------+----------+-----------------------------------------+------------+

"""
#coding: utf-8
import os
import re
import sys
import cv2

from ._cvpath import save_dir_create
from .video_image_handler import basenaming, mono_frame_generator, multi_frame_generator_concat, count_frame_num, create_VideoWriter
from .drawing import draw_text_with_bg, draw_bboxes_create
from .tracking import tracker_create, BBoxLogger
from ..utils.generic_utils import now_str, flatten_dual, int2ordinal, handleKeyError
from ..utils.print_utils import pretty_3quote, tabulate
from ..utils._colorings import toRED, toBLUE, toGREEN, toACCENT

def cv2key2chr(key):
    """Convert a key event into a Unicode string or an easy-to-understand string.

    Args:
        key (int) : The key event. (return of ``cv2.waitKey`` )

    Returns:
        (str) : a Unicode string of one character or an easy-to-understand string.

    Examples:
        >>> from pycharmers.opencv import cv2key2chr
        >>> import cv2
        >>> import numpy as np
        >>> from pycharmers.opencv import cv2key2chr
        ...  
        >>> winname = "cv2key2chr"
        >>> image = np.random.randint(low=0, high=255, size=(200,200,3), dtype=np.uint8)
        >>> while True:
        ...     key = cv2.waitKey(1)
        ...     cv2.imshow(winname=winname, mat=image)
        ...     if key!=-1: print(key, cv2key2chr(key))
        ...     if key==27: break
        >>> cv2.destroyWindow(winname=winname)
    """
    char = chr(key) if 0<=key<=0x10ffff else ""
    char2mean = {
        "\x08" : "<delete>",
        "\r"   : "<enter>",
        "\x1b" : "<esc>",
        " "    : "<space>",
        "\t"   : "<tab>",
        "\x00" : "<modifier>",
    }
    return char2mean.get(char, char)


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
    "FRAME" : ["To '{name}' frame", {
        "advance": "w", 
        "back": "b", 
        "jump": "@",
    }],
    "RANGE" : ["To select range '{name}'", {
        "start": "s",
        "end": "e",
    }],
    "TAKE" : ["To take '{name}'",{
        "picture": "p", 
        "video": "v"
    }],
}
DEFAULT_REALTIME_KEYS = {
    "TAKE" : ["To take '{name}'",{
        "picture": "p", 
        "video": "v"
    }],   
}
DEFAULT_TRACKING_KEYS = {
    "TRACKING" : ["To track '{name}'", {
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
        self.groups = []
        self.info_table = []
        self.cv_keys = cv_keys
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

    def update(self, other):
        """Update using other instance.

        Args:
            other (cvKeys) : Instance of :class:`cvKeys <pycharmers.opencv.windows.cvKeys>`
        """
        for group,(fmt,keys) in other.cv_keys.items():
            if group not in self.groups:
                self.set_keys(group=group, fmt=fmt, **keys)

    def set_keys(self, group, fmt, **keys):
        """Set keys.

        Args:
            group (str) : A group name. (ex. ``"MOVING"`` )
            fmt (str)   : How to describe group keys. Need to contain "{name}" (ex. ``"To move the window to the {name}"`` )
            keys (dict) : ``{name1:key1, name2:key2, ...}``
                        * name (str)  : A name in the ``group`` . (ex. ``"left"`` )
                        * key (str)   : A key corresponding to the ``name`` . (ex. ``"l"``)
        """
        group = group.upper()
        self.groups.append(group)
        for i, (name,key) in enumerate(keys.items()):
            self.info_table.append([toRED(group) if i==0 else "", fmt.format(name=toGREEN(name)), f"press {toBLUE(key)}"])
            setattr(self, f"{group}_{name.upper()}_KEY", key)
        setattr(self.__class__, f"{group}_KEYS", property(fget=lambda self: self._get_group_keys(group=group)))

    def describe(self):
        """Describe Key information."""
        tabulate(self.info_table, headers=["group", f"description ('{toGREEN('name')}')", "key"], tablefmt="grid")

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
        >>> cv2.imshow("Lena", cv2.imread(SAMPLE_LENA_IMG))
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
        >>> cv2.imshow("Lena", cv2.imread(SAMPLE_LENA_IMG))
        >>> val = wait_for_choice(*list("ltrb"))
        >>> cv2.destroyAllWindows()
    """
    max_val = len(choices)-1
    tabulate([[i,c] for i,c in enumerate(choices)], headers=["Input", "Choice"], tablefmt="pretty")
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

    def describe(self):
        """Describe Key info."""
        self.cvKey.describe()

    def destroy(self):
        """Do the necessary processing at the end."""
        for dirname in [self.img_save_dir, self.video_save_dir]:
            if sum(os.path.getsize(f) for f in os.listdir(dirname) if os.path.isfile(f))==0:
                os.removedirs(dirname)
                print(f"{toBLUE(dirname)} is deleted. (because it is empty)")
        cv2.destroyWindow(self.winname)

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
        if key in cvKey.BASE_KEYS_ORD:
            if key == cvKey.BASE_QUIT_KEY_ORD:
                is_break = True
                self.destroy()
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

class RealTimeWindow(cvWindow):
    """OpenCV window for RealiTime Video.

    Args:
        ext (str)  : File extension. (default= ``".jpg"`` )
        cam (int)  : The id of the web camera.

    Attributes:
        basenames (str)            : Concatenate of the final components of ``path``
        gen (gen)                  : ``cv2.VideoCapture(cam)``
        crt_frame (ndarray)        : The current image.
        crt_fname (str)            : The current image name.
        is_capture (bool)          : Whether capturing or not.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import RealTimeWindow
        >>> window = RealTimeWindow()
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    def __init__(self, winname=None, dirname=None, ext=".jpg", move_distance=10, expansion_rate=1.1, cam=0, cvKey=cvKeys(**DEFAULT_REALTIME_KEYS)):
        self.basenames = "realtime"
        self.ext = ext
        super().__init__(
            winname=winname,
            dirname=dirname,
            move_distance=move_distance,
            expansion_rate=expansion_rate,
            cvKey=cvKeys(**DEFAULT_CV_KEYS),
        )
        self.cvKey.update(cvKey)
        self.gen = cv2.VideoCapture(cam)
        _, self.crt_frame = self.gen.read()
        self.crt_fname = now_str()
        self.show()
        self.is_capture = False

    def show(self, mat=None):
        """Displays an image in the specified window. (``self.winname``)
        
        Args:
            mat (np.ndarray): Image to be shown.
        """
        if mat is None: mat = self.crt_frame
        draw_text_with_bg(
            img=mat, text=self.crt_fname,
            org=(50, 50), fontFace=1,
            fontScale=3, color=(0,0,0), bgcolor=(255,255,255),
            color_type="css4", thickness=1,
        )
        super().show(mat)

    def destroy(self):
        self.gen.release()
        super().destroy()

    def recieveKey(self, key):
        """Response according to Recieved key.

        Args:
            key (int): Input Key. (= ``cv2.waitKey(0)``)

        Returns:
            is_break (bool) Whether loop break or not. If break, destroy the window.
        """
        is_break = False
        cvKey = self.cvKey
        
        if self.is_capture:
            cv2.imwrite(filename=os.path.join(self.video_save_dir, self.crt_fname), img=self.crt_frame)

        # Take a picture of the current frame.
        if key in cvKey.TAKE_KEYS_ORD:
            if key == cvKey.TAKE_PICTURE_KEY_ORD:
                cv2.imwrite(filename=os.path.join(self.img_save_dir, self.crt_fname), img=self.crt_frame)
                print(f"Take a screenshot of {self.crt_fname} frame.")
            elif key == cvKey.TAKE_VIDEO_KEY_ORD:
                end, start = ("start", "end")[:: 1 if self.is_capture else -1]
                self.is_capture = not self.is_capture
                print(f"{start.capitalize()} taking a video. (If you want to {end}, please press {toBLUE(cvKey.TAKE_VIDEO_KEY)} again.)")            
        # Super Class function.
        else:
            is_break = super().recieveKey(key)
        if is_break:
            self.gen.release()
        else:
            _, self.crt_frame = self.gen.read()
            self.crt_fname = now_str()
            self.show()
        return is_break

class FrameWindow(cvWindow):
    """OpenCV window for Frames (images or video).

    Args:
        path (str) : path to video file, or directory which stores sequential images.
        ext (str)  : File extension. (default= ``".jpg"`` )

    Attributes:
        basenames (str)            : Concatenate of the final components of ``path``
        input_path (tuple)         : ``path``
        frame_generator (function) : function which generates sequential frames.
                                        - If ``len(path)==1`` -> :py:func:`mono_frame_generator <pycharmers.opencv.video_image_handler.mono_frame_generator>`
                                        - Otherwise -> :py:func:`multi_frame_generator_concat <pycharmers.opencv.windows.cvKeys.multi_frame_generator_concat>`
        gen (gen)                  : Generator created by ``frame_generator``
        total_num (int)            : The total number of frames.
        crt_frame_no (int)         : The current number of frames. (1-based index.)
        crt_frame (ndarray)        : The current image.
        range_start (int)          : Start number in the selected range.
        range_end (int)            : End number in the selected range.

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import FrameWindow, SAMPLE_VTEST_VIDEO
        >>> window = FrameWindow(SAMPLE_VTEST_VIDEO)
        >>> while True:
        ...     key = cv2.waitKey(0)
        ...     is_break = window.recieveKey(key)
        ...     if is_break:
        ...         break
        >>> cv2.destroyAllWindows()
    """
    def __init__(self, *path, winname=None, dirname=None, ext=".jpg", move_distance=10, expansion_rate=1.1, cvKey=cvKeys(**DEFAULT_FRAME_KEYS)):
        self.basenames = ".".join([basenaming(p) for p in path])
        self.ext = ext
        super().__init__(
            winname=winname,
            dirname=dirname,
            move_distance=move_distance,
            expansion_rate=expansion_rate,
            cvKey=cvKeys(**DEFAULT_CV_KEYS),
        )
        self.cvKey.update(cvKey)
        self.input_path = path
        self.frame_generator = {
            True  : mono_frame_generator,
            False : multi_frame_generator_concat,
        }[len(path)==1]
        self.gen = self.frame_generator(*path)
        self.total_num = count_frame_num(path[0])
        self.range_start = self.range_end = None
        self.crt_frame = self.gen.__next__()
        self.crt_frame_no = 1 # 1-based index.
        self.show()

    def fnaming(self, *no, ext=None):
        """Naming the file based on the number of frame.

        Args:
            no (int)  : Index of the frame.
            ext (str) : File extension.
        """
        ext = ext or self.ext
        if len(no)==1:
            name = f"{int2ordinal(no[0])}"
        elif len(no)==2:
            start, end = no
            name = f"{int2ordinal(start)}-{int2ordinal(start)}"
        return f"{self.basenames}_{name}_outof_{self.total_num}{ext}"

    def show(self, mat=None):
        """Displays an image in the specified window. (``self.winname``)
        
        Args:
            mat (np.ndarray): Image to be shown.
        """
        if mat is None: mat = self.crt_frame
        draw_text_with_bg(
            img=mat, text=f"{self.crt_frame_no}/{self.total_num}",
            org=(50, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=1, color=(0,0,0), bgcolor=(255,255,255),
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
                self.crt_frame_no = min(self.total_num, self.crt_frame_no+1)
            elif key == cvKey.FRAME_BACK_KEY_ORD:
                self.crt_frame_no = max(1, self.crt_frame_no-1)
            elif key == cvKey.FRAME_JUMP_KEY_ORD:
                frame_no = int(wait_for_input(fmt="Jump to {val} / " + f"{self.total_num} frame."))
                self.crt_frame_no = max(1, min(int(frame_no), self.total_num))
            self.gen = self.frame_generator(*self.input_path, frame_no=self.crt_frame_no-1)
            self.crt_frame = self.gen.__next__()
            self.show()
        # Do range processing
        elif key in cvKey.RANGE_KEYS_ORD:
            target, other = ("range_start", "range_end")[:: 1 if key == cvKey.RANGE_START_KEY_ORD else -1]
            self.__dict__[target] = self.crt_frame_no
            print(f"{target}: {int2ordinal(self.crt_frame_no)} frame.")
            if self.__dict__[other] is not None:
                self.range_processing()
        # Take a picture of the current frame.
        elif key == cvKey.TAKE_PICTURE_KEY_ORD:
            cv2.imwrite(filename=os.path.join(self.img_save_dir, self.fnaming(self.crt_frame_no)), img=self.crt_frame)
            print(f"Take a screenshot of {int2ordinal(self.crt_frame_no)} frame.")
        # Super Class function.
        else:
            is_break = super().recieveKey(key)
        return is_break

    def range_processing(self):
        """Select a range and process the image or video of that part."""
        start = self.range_start
        end = self.range_end
        span = end-start+1
        if span>0:
            cvKey = self.cvKey
            print(*pretty_3quote(f"""
            # You select {start}-{end} frame
            * press '{toBLUE(cvKey.TAKE_VIDEO_KEY)}' to extract a video.
            * press '{toBLUE(cvKey.TAKE_PICTURE_KEY)}' to shot all frames in the range.
            """))
            gen = self.frame_generator(*self.input_path, frame_no=start-1)
            total_num = self.total_num
            while True:
                key = cv2.waitKey(0)
                handleKeyError(lst=cvKey.TAKE_KEYS, key=chr(key))
                if key == cvKey.TAKE_PICTURE_KEY_ORD:
                    for i,frame in enumerate(gen):
                        current = start+i
                        fn = f"{self.basenames}.{current}.out.of.{total_num}.jpg"
                        cv2.imwrite(filename=os.path.join(self.img_save_dir, self.fnaming(current)), img=frame)
                        if current >= end: break
                    print(f"Take a screenshots from {int2ordinal(start)} frame to {int2ordinal(end)} frame.")
                    break
                elif key == cvKey.TAKE_VIDEO_KEY_ORD:
                    out_video = create_VideoWriter(
                        in_path=self.input_path[0],
                        out_path=os.path.join(self.video_save_dir, self.fnaming(start, end, ext=".mp4"))
                    )
                    for i,frame in enumerate(gen):
                        out_video.write(frame)
                        if start+i >= end: break
                    out_video.release()
                    print(f"Extract a video from {int2ordinal(start)} frame to {int2ordinal(end)} frame.")
                    break
            self.range_start = self.range_end = None
        else:
            print(f"{toGREEN('range_start')} must be an earlier frame than {toGREEN('range_end')}.")

class TrackingWindow(FrameWindow, RealTimeWindow):
    """OpenCV window for Trackings (images or video).

    Examples:
        >>> import cv2
        >>> from pycharmers.opencv import TrackingWindow, SAMPLE_VTEST_VIDEO
        >>> window = TrackingWindow(path=SAMPLE_VTEST_VIDEO, tracker="boosting", coord_type="xywh")
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
        self.gen = self.frame_generator(*self.input_path, frame_no=self.crt_frame_no)
        if min((bbox[-2:])) == 0:
            bbox = cv2.selectROI(windowName=self.init_bbox_winname, img=frame, showCrosshair=True, fromCenter=False)
        else:
            frame = self.draw_bboxes(frame=frame, bboxes=bbox, info={"text": "initial"})  
            cv2.imshow(self.init_bbox_winname, frame)
        self.tracker.init(frame, bbox) 
        self.logger.add_bboxes(no=self.crt_frame_no, bboxes=bbox)
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
                self.gen = self.frame_generator(*self.input_path, frame_no=self.crt_frame_no-1)
                frame = self.gen.__next__()
                self.bbox = cv2.selectROI(windowName=self.winname + "_initial_bbox", img=frame, showCrosshair=True, fromCenter=False)
                self.tracker.init(frame, self.bbox) 
            else:
                for frame in self.gen:
                    self.crt_frame_no += 1
                    track, bbox = self.tracker.update(frame)
                    self.logger.add_bboxes(no=self.crt_frame_no, bboxes=bbox)
                    if track:
                        bbox = [int(e) for e in bbox]
                        frame = self.draw_bboxes(frame=frame, bboxes=bbox)
                    else:
                        draw_text_with_bg(
                            img=frame, text="failure", org=(50,50),
                            fontFace=cv2.FONT_HERSHEY_COMPLEX, fontScale=1,
                            color="red", bgcolor="white", color_type="css4",
                            thickness=1,
                        )
                    self.show(frame)
                    k = cv2.waitKey(1)
                    if k==cvKey.TRACKING_STOP_KEY_ORD: break
        else:
            is_break = super().recieveKey(key)
        return is_break
