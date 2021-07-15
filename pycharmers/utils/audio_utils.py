#coding: utf-8
import os
import subprocess
import moviepy.editor as mp
from ._colorings import toBLUE, toRED

from typing import Optional

def synthesize_audio(video_path:str, audio_path:str, out_path:Optional[str]=None, use_moviepy:bool=False) -> str:
    """Use ``ffmpeg`` directly or ``moviepy`` to synthesize audio (@ ``audio_path``) to video (@ ``video_path``)

    Args:
        video_path (str)                   : The path to video fiile.
        audio_path (str)                   : The path to audio (video) fiile.
        out_path (Optional[str], optional) : The path to the created video (with audio) file. Defaults to ``None``.
        use_moviepy (bool)                 : Whether to use ``moviepy`` to synthesize audio or not. Defaults to ``True``

    Returns:
        str: The path to the created video (with audio) file.

    Raises:
        FileNotFoundError: When ``audio_path`` is not found.
        TypeError        : When there is no audio in ``audio_path``

    Examples:
        >>> from pycharmers.utils import synthesize_audio
        >>> # Prepare Audio file (.mp3)
        >>> synthesize_audio(audio_path="sound.mp3", video_path="no_sound.mp4")
        >>> # Prepare Video with Audio file (.mp4)
        >>> synthesize_audio(audio_path="sound.mp4", video_path="no_sound.mp4")
    """
    root, ext = os.path.splitext(audio_path)
    if ext not in [".mp3", ".wav"]:
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"No such file '{toBLUE(audio_path)}'")
        audio_clip = mp.VideoFileClip(audio_path).subclip()
        audio_path = root + ".mp3"
        if audio_clip.audio is None:
            raise TypeError(f"There is no audio in {toBLUE(audio_path)}")
        audio_clip.audio.write_audiofile(audio_path)
        print(f"Audio file (at {toBLUE(audio_path)}) is created.")
    if out_path is None:
        out_path = f"_synthesized".join(os.path.splitext(video_path))
    if use_moviepy:
        clip = mp.VideoFileClip(video_path).subclip()
        clip.write_videofile(
            out_path,
            audio=audio_path,
            codec='libx264',
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
    else:
        command = f"ffmpeg -y -i {video_path} -i {audio_path} -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 {out_path}"
        print(f"Run the following command:\n$ {command}")
        subprocess.call(command, shell=True)
    print(f"Synthesized video file (at {toBLUE(out_path)}) is created.")