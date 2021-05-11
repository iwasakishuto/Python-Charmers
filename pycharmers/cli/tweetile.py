# coding: utf-8
import os
import sys
import argparse
import numpy as np
from PIL import Image

from ..utils.generic_utils import filenaming
from ..utils._colorings import toBLUE

def tweetile(argv=sys.argv[1:]):
    """Divide one image into three so that you can tweet beautifully.

    Args:
        path (str) : Path to the input image.

    Note:
        When you run from the command line, execute as follows::
        
        $ tweetile path/to/image.jpg

    +--------------------------------------------+--------------------------------------------+--------------------------------------------+
    |                                                                  Size                                                                |
    +============================================+============================================+============================================+
    |                                                .. image:: _images/cli.tweetile-size.jpg                                              |
    +--------------------------------------------+--------------------------------------------+--------------------------------------------+


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
    parser = argparse.ArgumentParser(prog="tweetile", description="Tile one image for tweet.", add_help=True)
    parser.add_argument("path", type=str, help="Path to the input image.")
    args = parser.parse_args(argv)
    
    path = args.path
    img_pil = Image.open(path).resize(size=(1132, 636), resample=Image.LANCZOS)
    img_arr = np.asarray(img_pil)

    root_ext = os.path.splitext(path)
    img_paths = [filenaming(f".{i}".join(root_ext)) for i in range(1,4)]
    for img_path in img_paths:
        print(f"Save image at {toBLUE(img_path)}")
    Image.fromarray(np.uint8(img_arr[:,:564]   )).convert("RGB").save(img_paths[0], quality=95)
    Image.fromarray(np.uint8(img_arr[:316,568:])).convert("RGB").save(img_paths[1], quality=95)
    Image.fromarray(np.uint8(img_arr[320:,568:])).convert("RGB").save(img_paths[2], quality=95)