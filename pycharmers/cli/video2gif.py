#coding: utf-8
import os
import sys
import cv2
import argparse
from PIL import Image

from ..utils._colorings import toBLUE, toGREEN
from ..utils.argparse_utils import ListParamProcessorCreate
from ..utils.generic_utils import filenaming
from ..utils.print_utils import pretty_3quote
from ..utils.monitor_utils import ProgressMonitor

def video2gif(argv=sys.argv[1:]):
    """Convert Video into Gif.

    Args:
        video (str)      : Path to the video.
        --gif (str)      : Path to the output image.
        --resize (int)   : Enter a size separated by a comma ( ``width`` , ``height`` )
        --loop (int)     : How many times gif image loops.
        --speed (int)    : How many images will pass to get one. (The higher the number, the faster the speed).
        --twitter (bool) : Whether you want to run for tweet. ( ``resize`` will be ( ``1300`` , ``730`` ) )

    Note:
        When you run from the command line, execute as follows::
        
        $ video2gif path/to/video.mp4 --gif path/to/gif.gif --twitter
    """
    parser = argparse.ArgumentParser(prog="video2gif", description="Convert Video into Gif.", add_help=True)
    parser.add_argument("video",      type=str, help="Path to the video.")
    parser.add_argument("--gif",      type=str, help="Path to the output image.")
    parser.add_argument("--resize",   action=ListParamProcessorCreate(type=int), help="Enter a size separated by a comma (width,height)")
    parser.add_argument("--loop",     type=int, default=0, help="How many times gif image loops.")
    parser.add_argument("--speed",    type=int, default=5, help="How many images will pass to get one. (The higher the number, the faster the speed).")
    parser.add_argument("--twitter",  action="store_true", help="Whether you want to run for tweet. ( ``resize`` will be ( ``1300`` , ``730`` ) ).")
    args = parser.parse_args()

    video_path = args.video
    gif_path = args.gif
    resize = args.resize
    loop = args.loop
    speed = args.speed
    
    # === Load video & Get Video Information ===
    video   = cv2.VideoCapture(video_path)
    width   = video.get(cv2.CAP_PROP_FRAME_WIDTH)
    height  = video.get(cv2.CAP_PROP_FRAME_HEIGHT)
    fps     = video.get(cv2.CAP_PROP_FPS)
    count   = video.get(cv2.CAP_PROP_FRAME_COUNT)
    num_gif = int(1+(count-1)//speed)

    if gif_path is None:
        root, ext = os.path.splitext(video_path)
        gif_path = root + ".gif"
    gif_path = filenaming(name=gif_path)
    if args.twitter:
        resize = (1300, 730)
    elif resize is None:
        resize = (width, height)

    print(*pretty_3quote(f"""
    * Video Path   : {toBLUE(video_path)}
    * Gif   Path   : {toBLUE(gif_path)}
    * Frame Width  : {toGREEN(width )} -> {toBLUE(resize[0])} [px]
    * Frame Height : {toGREEN(height)} -> {toBLUE(resize[1])} [px]
    * Video Length : {toGREEN(f"{count/fps:.2f}")} [s]
    * FPS          : {toGREEN(f"{fps:.2f}")} [n/s]
    * Frame Count  : {toGREEN(count )} [n]
    * Speed        : {toGREEN(speed)} [n/include]
    → {toGREEN(num_gif)} frames will be included in GIF.
    """))

    i = 0
    images = []
    monitor = ProgressMonitor(max_iter=count, barname="video2gif")
    while True:
        ret, img_bgr = video.read()
        if img_bgr is None: 
            break
        elif i%speed==0:        
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            img_pillow = Image.fromarray(img_rgb).resize(size=resize, resample=Image.LANCZOS).quantize(method=0)
            images.append(img_pillow)
        i+=1
        monitor.report(i, frame_No=i)
    monitor.remove()
    images[0].save(
        fp=gif_path, 
        format="gif", 
        save_all=True, 
        append_images=images[1:], 
        loop=0
    )