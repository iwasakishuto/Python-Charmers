# coding: utf-8
import cv2
import os
import sys
import warnings
import argparse
import numpy as np
from PIL import Image

from typing import Any,Tuple
from nptyping import NDArray

from ..utils._colorings import toBLUE,toGREEN
from ..utils.generic_utils import filenaming
from ..utils.monitor_utils import ProgressMonitor

def tweetile(argv=sys.argv[1:]):
    """Divide one image into three so that you can tweet beautifully.

    Args:
        path (str)      : Path to the input image.
        --quality (int) : The image quality, on a scale from ``1`` (worst) to ``95`` (best). Defaults to ``95``.
        --loop (int)    : How many times gif image loops. Defaults to ``0``. (infinite loop.)

    Note:
        When you run from the command line, execute as follows::
        
        $ tweetile path/to/filename.jpg --quality 75
        $ tweetile path/to/filename.gif --loop 0

    +-----------------------------------------------+-----------------------------------------------+
    |                                            Example                                            |
    +===============================================+===============================================+
    | .. image:: _images/cli.tweetile-shingeki1.gif | .. image:: _images/cli.tweetile-shingeki2.gif |
    +                                               +-----------------------------------------------+
    |                                               | .. image:: _images/cli.tweetile-shingeki3.gif |
    +-----------------------------------------------+-----------------------------------------------+
    
    This movie is from :tw:`@anime_shingeki`

    .. tweet:: https://twitter.com/anime_shingeki/status/1376196378624282625
    """
    parser = argparse.ArgumentParser(prog="tweetile", description="Tile one image for tweet.", add_help=True)
    parser.add_argument("path",      type=str, help="Path to the input image.")
    parser.add_argument("--quality", type=int, default=95, help="The image quality, on a scale from 1 (worst) to 95 (best). Defaults to 95.")
    parser.add_argument("--loop",    type=int, default=0, help="How many times gif image loops. Defaults to 0. (infinite loop.)")
    args = parser.parse_args(argv)
    
    path = args.path
    quality = args.quality
    loop = args.loop
    root,ext = os.path.splitext(path)
    paths = [filenaming(f"{root}_{i}{ext}") for i in range(1,4)]

    if ext == ".gif":
        images_list = [[],[],[]]
        cap = cv2.VideoCapture(path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        monitor = ProgressMonitor(max_iter=frame_count, barname="tweetile")
        for i in range(1,frame_count+1):
            is_ok,img_bgr = cap.read()
            if (not is_ok) or (img_bgr is None):
                break
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            images = divideInto3forTweet(img_rgb)
            for j in range(len(images_list)):
                images_list[j].append(images[j])
                images[j].save(f"{j}/{i:>03}.png")
            monitor.report(i)
        monitor.remove()
        for images,path in zip(images_list, paths):
            images[0].save(
                fp=path,
                format="gif", 
                save_all=True, 
                append_images=images[1:], 
                loop=loop,
            )
            print(f"Saved gif at {toBLUE(path)}")
    else:
        img_arr = np.asarray(Image.open(path).resize(size=(1132, 636), resample=Image.LANCZOS), dtype=np.uint8)
        images = divideInto3forTweet(img_arr)
        for img,path in zip(images, paths):
            img.save(path, quality=quality)
            print(f"Saved image at {toBLUE(path)}")

def divideInto3forTweet(img_arr:NDArray[(636,1132,Any), np.uint8]) -> Tuple[Image.Image,Image.Image,Image.Image]:
    """Divide Image into 3 for Tweet

    +--------------------------------------------+
    |                     Size                   |
    +============================================+
    |   .. image:: _images/cli.tweetile-size.jpg |
    +--------------------------------------------+

    Args:
        img_arr (NDArray[(636,1132,Any), np.uint8]): Input image array (RGB)

    Returns:
        Tuple[Image.Image,Image.Image,Image.Image]: A tuple of each Image object divided into three.

    Examples:
        >>> import cv2
        >>> from pycharmers.cli.tweetile import divideInto3forTweet
        >>> img_bgr = cv2.imread("cli.tweetile-before.jpg")
        >>> img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        >>> for i,img in enumerate(divideInto3forTweet(img_rgb), start=1):
        ...     img.save(f"cli.tweetile-after{i}.jpg", quality=95)

    +--------------------------------------------+--------------------------------------------+--------------------------------------------+
    |                                                               Example                                                                |
    +============================================+============================================+============================================+
    |                                     Before |                                          After                                          |
    +--------------------------------------------+--------------------------------------------+--------------------------------------------+
    | .. image:: _images/cli.tweetile-before.jpg | .. image:: _images/cli.tweetile-after1.jpg | .. image:: _images/cli.tweetile-after2.jpg |
    +                                            +                                            +--------------------------------------------+
    |                                            |                                            | .. image:: _images/cli.tweetile-after3.jpg |
    +--------------------------------------------+--------------------------------------------+--------------------------------------------+
    """
    h,w,ch = img_arr.shape
    if ((h!=636) or (w!=1132)):
        warnings.warn(f"Resize the input image from {toGREEN((h,w,ch))} to {toGREEN((636,1132,ch))}.")
        img_arr = cv2.resize(img_arr, dsize=(1132,636))
    images = [img_arr[:,:564], img_arr[:316,568:], img_arr[320:,568:]]
    return tuple(Image.fromarray(np.uint8(img)) for img in images)
