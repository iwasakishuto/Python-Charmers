#coding: utf-8
import os
import sys
import re
import cv2

from . import SAVE_PATH
from .video_image_handler import (basenaming, mono_frame_generator, multi_frame_generator_concat,
                                 count_frame_num, create_VideoWriter)
from .drawing import draw_text_with_bg

# KEYS for `cvWindow`
MOVING_KEYS     = [ord("h"), ord("l"), ord("j"), ord("k")]
ABS_POS_KEYS    = [ord("o")]
FULLSCREEN_KEYS = [ord("f")]
RATIO_KEYS      = [ord("+"), ord("-")]
QUIT_KEYS       = [ord("\x1b"), ord("q")] # "\x1b" = <esc>
INFO_KEYS       = [ord("i")]
# WAIT FOR NUMBER
ENTER_KEYS      = [ord("\r")]   # <enter>
NUMBER_KEYS     = [i for i in range(ord("0"), ord("9")+1)]
# KEYS for `frameWindow`.
FRAME_KEYS      = [ord("w"), ord("b"), ord("@")]
DELETE_KEYS     = [ord("\x08")] # <delete>
RANGE_KEYS      = [ord("s"), ord("e")]
TAKE_PIC_KEYS   = [ord("p")]
TAKE_VIDEO_KEYS = [ord("v")]

def print_alpha2key():
    alpha2key = {}
    for name,vals in globals().items():
        if name.endswith("_KEYS"):
            alpha2key.update({chr(e): name for e in vals if re.match(r"[a-z]", chr(e))})

    for i in range(26):
        alphabet = chr(ord('a')+i)
        print(f"{alphabet}: {alpha2key.get(alphabet, '-')}")

def waitForNumber(format_="Your input: {}"):
    current_num = ""
    template = "\033[2K\033[G" + format_
    sys.stdout.write(template.format(current_num))
    sys.stdout.flush()
    key = cv2.waitKey(0)
    while key not in ENTER_KEYS:
        if key in DELETE_KEYS:
            current_num = current_num[:-1]
        elif key in NUMBER_KEYS:
            current_num += chr(key)
        sys.stdout.write(template.format(current_num))
        sys.stdout.flush()
        key = cv2.waitKey(0)
    print()
    if len(current_num) == 0:
        current_num = waitForNumber(format_=format_)
    return int(current_num)

def waitForInput(format_="Your input: %s"):
    current_val = ""
    format_ = "\033[2K\033[G" + format_
    sys.stdout.write(format_ % current_val)
    sys.stdout.flush()
    key = cv2.waitKey(0)
    while key not in ENTER_KEYS:
        if key in DELETE_KEYS:
            current_val = current_val[:-1]
        else:
            current_val += chr(key)
        sys.stdout.write(format_ % current_val)
        sys.stdout.flush()
        key = cv2.waitKey(0)
    print()
    return current_val

def waitTochoice(*keys):
    num_choices = len(keys)
    max_len = len(max(keys, key=len))
    int2key = dict(zip(range(num_choices), keys))

    print("\nPlease input the corresponding number.")
    for i,k in int2key.items():
        print(f" - {k:<{max_len}}: {i}")

    while True:
        i = waitForNumber()
        if 0 <= i < num_choices:
            break
        else:
            print(f"* Please input from 0 to {num_choices-1} (got {i})")
    return keys[i]

class cvWindow():
    """
    [ Window & Image Location ]
    - Ix,Iy,Iw,Ih = cv2.getWindowImageRect(winname)
    - cv2.moveWindow(winname, Wx, Wy)
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
    """
    No = 0

    def __init__(self, winname=None, move_distance=10, expansion_rate=1.1):
        cvWindow.No += 1
        if winname is None:
            winname = f"frame {cvWindow.No:>02}"
        self.winname = winname
        cv2.namedWindow(winname, cv2.WINDOW_NORMAL)

        self.move_distance = move_distance
        if expansion_rate <= 1.:
            expansion_rate += 1.
        self.expansion_rate = expansion_rate
        self.reduction_rate = 1./expansion_rate

        self.iIh = None
        self.iIw = None

    @property
    def frame_size(self):
        Wx,Wy,Fw,Fh = self.get_anchors()
        return (Fw,Fh)

    @property
    def image_size(self):
        _,_,Iw,Ih = cv2.getWindowImageRect(self.winname)
        return (Iw,Ih)

    def resizeWindow(self, H, W):
        cv2.resizeWindow(self.winname, (H,W))

    def moveWindow(self, x, y):
        cv2.moveWindow(self.winname, x, y)

    def getWindowImageRect(self):
        return cv2.getWindowImageRect(self.winname)

    def getWindowRect(self):
        Wx,Wy,Fw,Fh = self.get_anchors()
        Iw,Ih = self.image_size
        return (Wx,Wy,Iw+Fw*2,Ih+Fh*2)

    def align_TopLeft(self):
        cv2.moveWindow(self.winname, 0, 0)

    def get_anchors(self):
        """ Get the Wx,Wy,Fw,Fh """
        winname = self.winname
        # NOTE: In fact, get the current (Ix,Iy).
        Wx,Wy,_,_ = cv2.getWindowImageRect(winname)
        cv2.moveWindow(winname, Wx, Wy)
        # NOTE; In fact, get the (Ix+Fw,Iy+Fw) in the initial window.
        Ix,Iy,_,_ = cv2.getWindowImageRect(winname)
        Fw = Ix-Wx; Fh = Iy-Wy
        # NOTE: This is the real (Wx,Wy) in the initial window.
        Wx -= Fw; Wy -= Fh
        # Reset the window position.
        cv2.moveWindow(winname, Wx, Wy)
        return (Wx,Wy,Fw,Fh)

    def show(self, mat):
        if self.iIh is None or (self.iIh, self.iIw) != mat.shape[:2]:
            self.iIh, self.iIw, _ = mat.shape
            self.Ih, self.Iw, _ = mat.shape
            cv2.resizeWindow(self.winname, (self.iIh, self.iIw))
        cv2.imshow(self.winname, mat)

    def _ret_info(self):
        return f"""
        [Window Name {self.winname}]
        # Move window : {self.move_distance}px
        - To move left,  press 'h' .
        - To move right, press 'l' .
        - To move down,  press 'j' .
        - To move up,    press 'k' .
        # window position
        - To align top & left, press 'o' .
        - To make the window full screen, press 'f' .
        # Expansion & Reduction : {self.expansion_rate*100:.1f}%
        - To expand window, press '+' .
        - To shrink window, press '-' .
        # Quit
        - To quit, press 'q' or '<ESC>' .
        # Info
        - To get the window rectangle, press 'i' .
        """

    def describe(self):
        print(self._ret_info())

    def recieveKey(self, key):
        """
        @params key      : (int) Input Key. (= cv2.waitKey(1) )
        @return is_break : (bool) Whether loop break or not.
                           If break, destroy the window.
        """
        is_break = False
        winname = self.winname

        if key in QUIT_KEYS:
            cv2.destroyWindow(winname)
            is_break = True

        elif key in MOVING_KEYS:
            Wx,Wy,_,_ = self.get_anchors()

            if key == ord("h"):
                Wx-=self.move_distance
            elif key == ord("l"):
                Wx+=self.move_distance
            elif key == ord("j"):
                Wy+=self.move_distance
            else: # key == ord("k")
                Wy-=self.move_distance

            cv2.moveWindow(winname, Wx, Wy)

        elif key in RATIO_KEYS:
            if key == ord("+"):
                rate = self.expansion_rate
            else:
                rate = self.reduction_rate

            self.Ih = int(rate*self.Ih)
            self.Iw = int(rate*self.Iw)
            cv2.resizeWindow(winname, (self.Ih, self.Iw))

        elif key in INFO_KEYS:
            print(f"Window Rectangle: {self.getWindowRect()}")

        elif key in ABS_POS_KEYS:
            self.align_TopLeft()

        elif key in FULLSCREEN_KEYS:
            """
            cv2.WINDOW_NORMAL = 0
            cv2.WINDOW_FULLSCREEN = 1
            """
            cv2.setWindowProperty(
                winname=winname,
                prop_id=cv2.WND_PROP_FULLSCREEN,
                prop_value=1-cv2.getWindowProperty(
                    winname=winname,
                    prop_id=cv2.WND_PROP_FULLSCREEN,
                )
            )

        return is_break

class frameWindow(cvWindow):
    def __init__(self, *input_path, winname=None, move_distance=10, expansion_rate=1.1):
        self.name = "+".join([basenaming(path) for path in input_path])
        if winname is None:
            winname = self.name
        super().__init__(
                winname=winname,
                move_distance=move_distance,
                expansion_rate=expansion_rate
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
        self.start_ = None
        self.end_ = None
        self.show(self.gen.__next__())

    def show(self, mat):
        draw_text_with_bg(
            img=mat, text=f"{self.frame_num}/{self.total_num}",
            org=(50, 50), fontFace=cv2.FONT_HERSHEY_COMPLEX,
            fontScale=3, color=(0,0,0), bgcolor=(255,255,255),
            color_type="css4", thickness=1,
        )
        super().show(mat)

    def recieveKey(self, key):
        is_break = False
        if key in FRAME_KEYS:
            if key == ord("w"):
                if self.frame_num < self.total_num:
                    self.frame_num += 1
                else:
                    self.gen = self.frame_generator(
                        *self.input_path, frame_num=self.frame_num-1
                    )
            elif key == ord("b"):
                self.frame_num -= 1
                self.frame_num = max(1, self.frame_num)
                self.gen = self.frame_generator(
                    *self.input_path, frame_num=self.frame_num-1
                )
            elif key == ord("@"):
                frame_num = waitForNumber(format_="\033[2K\033[GJump to %s frame.")
                self.frame_num = max(1, min(int(frame_num), self.total_num))
                self.gen = self.frame_generator(
                    *self.input_path, frame_num=self.frame_num-1
                )
            self.show(self.gen.__next__())
        elif key in RANGE_KEYS:
            if key == ord("s"):
                self.start_ = self.frame_num
                print(f"start: {self.frame_num} frame.")
                if self.end_ is not None:
                    self.range_processing()
            elif key == ord("e"):
                self.end_ = self.frame_num
                print(f"end  : {self.frame_num} frame.")
                if self.start_ is not None:
                    self.range_processing()
        elif key in TAKE_PIC_KEYS:
            self.gen = self.frame_generator(
                *self.input_path, frame_num=self.frame_num-1
            )
            frame = self.gen.__next__()
            fn = f"{self.name}({self.frame_num}-out-of-{self.total_num}).png"
            cv2.imwrite(os.path.join(SAVE_PATH, fn), frame)
            print(f"Take a screenshot ({self.frame_num} frame)")
        else:
            is_break = super().recieveKey(key)
        return is_break

    def range_processing(self):
        start = self.start_
        end = self.end_
        span = end-start+1
        if span<0:
            print("`start` must be an earlier frame than `end`.")
        else:
            print(f"""
            # You select {start}-{end} frame
            - press 'v' to extract a video.
            - press 'p' to shot all frames in the range.
            """)
            gen = self.frame_generator(*self.input_path, frame_num=start-1)
            name = self.name
            total_num = self.total_num
            while True:
                key = cv2.waitKey(0)
                if key in TAKE_PIC_KEYS:
                    for i,frame in enumerate(gen):
                        current = start+i
                        fn = f"{name}({current}-out-of-{total_num}).png"
                        cv2.imwrite(os.path.join(SAVE_PATH, fn), frame)
                        if current >= end:
                            break
                    print(f"Take a screenshots from {start} frame to {end} frame.")
                    break
                elif key in TAKE_VIDEO_KEYS:
                    video_fn = f"{name}({start}-to-{end}-out-of-{total_num}).mp4"
                    out_video = create_VideoWriter(
                        in_path=self.input_path_,
                        out_path=os.path.join(SAVE_PATH, video_fn)
                    )
                    for i,frame in enumerate(gen):
                        out_video.write(frame)
                        if start+i >= end:
                            break
                    out_video.release()
                    print(f"Extract a video from {start} frame to {end} frame.")
                    break
                else:
                    print(f"Please select a key from {', '.join(TAKE_PIC_KEYS+TAKE_VIDEO_KEYS)}")

        self.start_ = None
        self.end_ = None

    def _ret_info(self):
        info  = super()._ret_info()
        info += f"""# Frame Control
        - To advance frame, press 'w' .
        - To back frame,    press 'b' .
        - To jump to frame, press '@' .
            Then,
            - To specify the frane, press 'number key' .
            - To delete character,  press '<delete>' .
            - To finish the entry,  press '<enter>' .
        # Video Editing
        - To take a screenshot, press 'p' .
        - When you deal with a contiguous range of video,
            - press 's', and 'e' to select the range.
            - press 'v' to extract a video.
            - press 'p' to shot all frames in the range.
        """
        return info