# coding: utf-8
import time
import pyautogui as pygui
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

from ._path import PYCHARMERS_ICON
from .monitor_utils import ProgressMonitor

class PortionSelector():
    """
	Args:
		resize_ratio (float) : How much to resize the screenshot. (∵ The default screenshot is too big)
    
    Attributes:
        root (Tk)         : Toplevel widget of Tk which represents mostly the main window of an application. It has an associated Tcl interpreter.
        canvas (Canvas)   : Canvas widget to display graphical elements like lines or text.
        ss (Image)        : A ScreenShot. You can retake using :meth:`retake_screenshot <pycharmers.utils.PortionSelector.retake_screenshot>` method.
        sstk (PhotoImage) : A Screenshot converted for display on ``tkinter``.
        portion (list)    : Selected Portion.

    Examples:
        >>> from pycharmers.utils import PortionSelector
        >>> ps = PortionSelector()
        >>> ps.run()
        >>> portion = ps.portion
    """
    def __init__(self, resize_ratio=2.):
        self.root = tk.Tk()
        self.root.title(self.__class__.__name__)
        self.root.tk.call("wm", "iconphoto", self.root._w, ImageTk.PhotoImage(file=PYCHARMERS_ICON))
        self.ss = self.retake_screenshot(sec=0)
        self.init(resize_ratio=resize_ratio)

    def init(self, resize_ratio=2):
        """Initialization"""
        self.resize_ratio = resize_ratio
        self.ssResize(dsize=[round(s/resize_ratio) for s in self.ssSize])
        self.portion = [0,0,0,0]

    def run(self):
        """Run the main loop"""
        w,h = self.ssSize
        self.canvas = tk.Canvas(self.root, bg="black", width=w, height=h)
        self.canvas.create_image(0, 0, image=self.sstk, anchor=tk.NW)
        self.canvas.pack()
        self.canvas.bind("<ButtonPress-1>",   self.get_start_point)
        self.canvas.bind("<Button1-Motion>",  self.draw_curt_rect)
        self.canvas.bind("<ButtonRelease-1>", self.release_action) 
        self.root.mainloop()

    def retake_screenshot(self, sec=3):
        """Retake the screenshot after ``sec`` seconds.
        
        Args:
            sec (int) : Retake a screenshot in ``sec`` seconds.

        Returns:
            Image : Taken screenshot.
        """
        sec = int(sec)
        if sec>0:
            monitor = ProgressMonitor(max_iter=sec)
            for it in range(sec):
                monitor.report(it, msg=f"Take in {sec-it-1} second.")
            monitor.report()
        return pygui.screenshot()

    @property
    def ssSize(self):
        """The size of ScreenShot."""
        return (self.ss.width, self.ss.height)

    def get_xywh(self):
        """Get portion of the original magnification."""
        x1,y1,x2,y2 = [round(p * self.resize_ratio) for p in self.portion]
        x1,x2 = (x1,x2) if x1<x2 else (x2,x1)
        y1,y2 = (y1,y2) if y1<y2 else (y2,y1)
        return [x1,y1,x2-x1,y2-y1]

    def ssResize(self, dsize):
        """Resize both screenshots ( ``self.ss``, ``self.sstk`` ).

        Args:
            dsize (tuple) : Resized screenshot size.
        """
        self.ss = self.ss.resize(size=dsize, resample=Image.BILINEAR)
        self.sstk = ImageTk.PhotoImage(self.ss)

    def get_start_point(self, evt):
        """Get the start point.

        Args:
            evt (Event) : Container for the properties of an event. 

        Examples:
            >>> from pycharmers.utils import PortionSelector
            >>> ps = PortionSelector()
            >>> ps.canvas.pack()
            >>> ps.canvas.bind("<ButtonPress-1>",   ps.get_start_point)
            >>> ps.canvas.bind("<Button1-Motion>",  "Action executed when Mouse is moving")
            >>> ps.canvas.bind("<ButtonRelease-1>", "Action executed when Button released")
            >>> ps.root.mainloop()
        """
        self.canvas.delete("portion")
        self.canvas.create_rectangle(evt.x, evt.y, evt.x+1, evt.y+1, outline="red", tag="portion")
        self.portion[:2] = [evt.x, evt.y]

    def draw_curt_rect(self, evt):
        """Drawing the current Rectangle.

        Args:
            evt (Event) : Container for the properties of an event. 

        Examples:
            >>> from pycharmers.utils import PortionSelector
            >>> ps = PortionSelector()
            >>> ps.canvas.pack()
            >>> ps.canvas.bind("<ButtonPress-1>",   "Action executed when Button Pressed")
            >>> ps.canvas.bind("<Button1-Motion>",  ps.draw_curt_rect)
            >>> ps.canvas.bind("<ButtonRelease-1>", "Action executed when Button released")
            >>> ps.root.mainloop()
        """
        start_x, start_y = self.portion[:2]
        ssw, ssh = self.ssSize
        end_x = max(min(ssw, evt.x), 0)
        end_y = max(min(ssh, evt.y), 0)
        self.canvas.coords("portion", start_x, start_y, end_x, end_y)
        self.portion[2:] = [end_x, end_y]

    def release_action(self, evt):
        """Drawing the current Rectangle.

        Args:
            evt (Event) : Container for the properties of an event. 

        Examples:
            >>> from pycharmers.utils import PortionSelector
            >>> ps = PortionSelector()
            >>> ps.canvas.pack()
            >>> ps.canvas.bind("<ButtonPress-1>",   "Action executed when Button Pressed")
            >>> ps.canvas.bind("<Button1-Motion>",  "Action executed when Mouse is moving")
            >>> ps.canvas.bind("<ButtonRelease-1>", ps.release_action)
            >>> ps.root.mainloop()
        """
        x,y,w,h = self.get_xywh() 
        msgBox = tk.messagebox.askquestion(
            title="Confirm Selected Portion", 
            message=f"[You chose the following location]\nStart Position : ({x}, {y})\nPortion Size   : ({w},{h})",
        )
        if msgBox=="yes":
            self.root.after("500", func=self.quit)

    def quit(self):
        self.root.quit()
        self.root.destroy()
