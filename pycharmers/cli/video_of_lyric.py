#coding: utf-8
import os
import cv2
import sys
import json
import argparse
import subprocess
import numpy as np
import moviepy.editor as mp
from PIL import Image

from ..utils._colorings import toBLUE, toGREEN, toACCENT
from ..utils.argparse_utils import ListParamProcessorCreate
from ..utils.generic_utils import now_str
from ..utils.monitor_utils import ProgressMonitor
from ..utils.pil_utils import draw_text_in_pil

def video_of_lyric(argv=sys.argv[1:]):
    """Create a lyric Video.

    Args:
        json (str)            : Path to parameter json file.
        --ttfontname (str)    : A filename or file-like object containing a TrueType font. If the file is not found in this filename, the loader may also search in other directories, such as the ``fonts/`` directory on Windows or ``/Library/Fonts/`` , ``/System/Library/Fonts/`` and ``~/Library/Fonts/`` on macOS.
        --margin (int)        : The margin size.
        --mode (str)          : Optional mode to use for color values.
        --fontsize (int)      : The font size.
        --fontwidth (int)     : The font width.
        --fontheight (int)    : The font height.
        --img-size (tuple)    : The image size.
        --bgRGB (tuple)       : he color of background image. (RGB)
        --textRGB (tuple)     : The color of text. (RGB)
        --alpha-range (float) : How many seconds to set alpha to 1 (maximum).
        --fps (float)         : The video fps.
        --span (int)          : The span between lyrics.

    .. code-block:: python
    
        >>> # Create a json.
        >>> import numpy as np
        >>> def func(word, start, end, indent='\\t'*4):
        ...     print(f'{indent}"words": "{word}",')
        ...     print(f'{indent}"seconds": {[round(e,3) for e in np.linspace(start, end, len(word))]},')


    .. code-block:: python

        >>> import json
        >>> from pycharmers.utils import dumps_json
        >>> with open("era-it-doo/era-it.json") as f:
        ...     data = json.load(f)
        >>> print(dumps_json(data))
        {
          "kwargs": {
            "ttfontname": "/Users/iwasakishuto/Library/Fonts/851MkPOP_002.ttf",
            "img_size": [
              360,
              640
            ],
            "fontsize": 38,
            "fontwidth": 30,
            "margin": 10,
            "bgRGB": [
              0,
              0,
              0,
              255
            ],
            "mode": "RGBA",
            "ret_position": "line"
          },
          "texts": [
            [{"words":"１日今日も、","seconds":[2.4, 2.624, 2.848, 3.072, 3.296, 3.52],"x":-1,"y":50},{"words":"こなした労働、","seconds":[4.1, 4.317, 4.533, 4.75, 4.967, 5.183, 5.4],"x":-1,"y":-1},{"words":"辛かったけど","seconds":[5.7, 5.96, 6.22, 6.48, 6.74, 7.0],"x":-1,"y":-1},{"words":"本当がんばったじゃん","seconds":[7.0, 7.222, 7.444, 7.667, 7.889, 8.111, 8.333, 8.556, 8.778, 9.0],"x":-1,"y":-1},{"words":"１日今日も、","seconds":[9.1, 9.38, 9.66, 9.94, 10.22, 10.5],"x":-1,"y":260},{"words":"いちいちどうこう、","seconds":[10.8, 10.962, 11.125, 11.288, 11.45, 11.612, 11.775, 11.938, 12.1],"x":-1,"y":-1},{"words":"いわれたけど","seconds":[12.3, 12.52, 12.74, 12.96, 13.18, 13.4],"x":-1,"y":-1},{"words":"本当にがんばったじゃん","seconds":[13.4, 13.59, 13.78, 13.97, 14.16, 14.35, 14.54, 14.73, 14.92, 15.11, 15.3],"x":-1,"y":-1}]
          ]
        }         

    Note:
        When you run from the command line, execute as follows::
        
        $ video_of_lyric dodo-era-it.json --audio dodo-era-it.mp4[.mp3]

    +--------------------------------------------+
    |                Sample                      |
    +============================================+
    | .. image:: _images/cli.video_of_lyric.gif  |
    +--------------------------------------------+
    """
    parser = argparse.ArgumentParser(prog="video_of_lyric", description="Create a lyric Video.", add_help=True)
    parser.add_argument("json",                type=str, help="Path to parameter json file.")
    parser.add_argument("--ttfontname",  type=str, default=None, help="A filename or file-like object containing a TrueType font. If the file is not found in this filename, the loader may also search in other directories, such as the ``fonts/`` directory on Windows or ``/Library/Fonts/`` , ``/System/Library/Fonts/`` and ``~/Library/Fonts/`` on macOS.")
    parser.add_argument("--margin",      type=int, default=None, help="The margin size.")
    parser.add_argument("--mode",        type=str, default=None, help="Optional mode to use for color values.")
    parser.add_argument("--fontsize",    type=int, default=None, help="The font size.")
    parser.add_argument("--fontwidth",   type=int, default=None, help="The font width.")
    parser.add_argument("--fontheight",  type=int, default=None, help="The font height.")
    parser.add_argument("--img-size",    action=ListParamProcessorCreate(type=int), default=None, help="The image size.")
    parser.add_argument("--bgRGB",       action=ListParamProcessorCreate(type=int), default=None, help="The color of background image. (RGB)")
    parser.add_argument("--textRGB",     action=ListParamProcessorCreate(type=int), default=None, help="The color of text. (RGB)")
    parser.add_argument("--alpha-range", type=float, help="The video length [s].", default=1.)
    parser.add_argument("--fps",         type=float, help="The video fps.", default=30.)
    parser.add_argument("--span",        type=int,   help="The span between lyrics", default=None)
    parser.add_argument("--audio",       type=str,   help="The audio path.", default=None)
    args = parser.parse_args(argv)

    json_path = args.json
    with open(json_path, mode="r") as f:
        data = json.load(f)

    args_kwargs = dict(args._get_kwargs())
    data_kwargs = data.get("kwargs", {})
    get_kwargs = lambda x,default=None:args_kwargs.get(x) or data_kwargs.get(x, default)
    img_size   = tuple(get_kwargs("img_size", default=[360,640])[:2])
    bgRGB      = tuple(get_kwargs("bgRGB", default=(0,0,0,255)))
    textRGB    = tuple(get_kwargs("textRGB", default=(255,255,255,255)))
    mode       = get_kwargs("mode", default="RGBA")
    margin     = get_kwargs("margin", default=10)
    fontsize   = get_kwargs("fontsize", default=40)
    fontwidth  = get_kwargs("fontwidth", default=None)
    fontheight = get_kwargs("fontheight", default=None)
    span       = get_kwargs("span", default=1)
    audio_path = get_kwargs("audio", default=None)
    alpha_range = args.alpha_range
    fps = args.fps
    spf = 1/fps
    kwargs = {
        "ttfontname": get_kwargs("ttfontname", default=""),
        "img_size": img_size,
        "fontsize": fontsize,
        "fontwidth": fontwidth,
        "fontheight": fontheight,
        "margin": margin,
        "bgRGB": bgRGB,
        "mode": mode,
        # "ret_position": "line",
    }
    text_data = data.get("texts", [[]])
    num_texts = len(text_data)
    sec_filter = []
    for i,page in enumerate(text_data):
        start, end = (1e16, 0)
        for line in page:
            secs = line.get("seconds", [])
            start = min(start, *secs)-alpha_range
            end   = max(end, *secs)
        sec_filter.append([i,start,end+alpha_range+span])
    duration = max([e[2] for e in sec_filter]) + alpha_range + 1
    num_frames = int(duration*fps)
    
    def set_pos(data, name, default):
        p = data.get(name, -1)
        if p==-1: p = default
        return p

    def set_fontcolor(start, sec, textRGB, alpha_range):
        fc = [0]*4
        fc[:3] = textRGB[:3]
        fc[3] = min(255, max(0, int((sec-start)/alpha_range*255)))
        return tuple(fc)

    params = {
        "duration" : duration,
        "alpha range" : alpha_range,
        "FPS": fps,
        "span": span,
        "audio": audio_path,
    }
    params.update(kwargs)
    print("[Parameters]")
    for k,v in params.items():
        print(f"* {toACCENT(k)}: {toGREEN(v)}")

    root, ext = os.path.splitext(json_path)
    video_path = f"{root}_{now_str()}.mp4"
    fourcc = cv2.VideoWriter_fourcc('m','p','4','v')
    out_video = cv2.VideoWriter(video_path, fourcc, fps, img_size)
    monitor = ProgressMonitor(max_iter=num_frames, barname="Editing")
    it = sec = 0
    while True:
        it+=1
        bg = Image.new(mode=mode, size=img_size, color=bgRGB)
        sec += spf
        for i,*_ in filter(lambda x:x[1]<= sec <x[2], sec_filter):
            texts = text_data[i]
            init_x = x = y = margin
            for j,line in enumerate(texts):
                words = line.get("words", "")
                startSecs = line.get("seconds", [])
                x = set_pos(data=line, name="x", default=x)
                y = set_pos(data=line, name="y", default=y)
                for w,start in zip(words, startSecs):
                    fc = set_fontcolor(start, sec, textRGB, alpha_range)
                    bg,(x,_) = draw_text_in_pil(text=w, img=bg, ret_position="word", textRGB=fc, x=x, y=y, **kwargs)
                y += fontsize
                x = init_x
            break
        out_video.write(np.asanyarray(bg.convert("RGB")))
        monitor.report(it, sec=f"{sec:.2f}/{duration}", text=f"{j+1}/{num_texts}")
        if sec>duration:
            break
    out_video.release()
    monitor.remove()
    print(f"{toBLUE(video_path)} (No Sound) is created.")

    if audio_path is not None:
        root, ext = os.path.splitext(audio_path)
        if ext!=".mp3":
            audio_clip = mp.VideoFileClip(audio_path).subclip()
            audio_path = root + ".mp3"
            audio_clip.audio.write_audiofile(audio_path)
            print(f"Audio file ({toBLUE(audio_path)}) is created.")
        video_with_audio_path = f"_audio".join(os.path.splitext(video_path))
        clip = mp.VideoFileClip(video_path).subclip()
        clip.write_videofile(
            video_with_audio_path, 
            audio=audio_path, 
            codec='libx264', 
            audio_codec='aac', 
            temp_audiofile='temp-audio.m4a', 
            remove_temp=True
        )
        command = [
            "ffmpeg", "-y", 
            "-i", video_path, 
            "-i", audio_path, 
            "-c:v", "copy", 
            "-c:a", "copy",
            video_with_audio_path,
        ]
        with open("ffmpeg.log", 'w') as f:
            process = subprocess.Popen(command, stderr=f)
        print(f"{toBLUE(video_with_audio_path)} (With Sound) is created.")