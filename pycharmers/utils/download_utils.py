# coding: utf-8
import os
import urllib

from .generic_utils import readable_bytes
from .monitor_utils import progress_reporthook_create
from .print_utils import pretty_3quote
from ._colorings import toBLUE, toRED, toGREEN

# Use Specific Opener
opener = urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
urllib.request.install_opener(opener)

CONTENT_ENCODING2EXT = {
    "x-gzip"                    : ".gz",
    "image/jpeg"                : ".jpg",
    "image/jpx"                 : ".jpx", 
    "image/png"                 : ".png",
    "image/gif"                 : ".gif",
    "image/webp"                : ".webp",
    "image/x-canon-cr2"         : ".cr2",
    "image/tiff"                : ".tif",
    "image/bmp"                 : ".bmp",
    "image/vnd.ms-photo"        : ".jxr",
    "image/vnd.adobe.photoshop" : ".psd",
    "image/x-icon"              : ".ico",
    "image/heic"                : ".heic",
}

CONTENT_TYPE2EXT = {
    "application/epub+zip"                  : ".epub",
    "application/zip"                       : ".zip",
    "application/x-tar"                     : ".tar",
    "application/x-rar-compressed"          : ".rar",
    "application/gzip"                      : ".gz",
    "application/x-bzip2"                   : ".bz2",
    "application/x-7z-compressed"           : ".7z",
    "application/x-xz"                      : ".xz",
    "application/pdf"                       : ".pdf",
    "application/x-msdownload"              : ".exe",
    "application/x-shockwave-flash"         : ".swf",
    "application/rtf"                       : ".rtf",
    "application/octet-stream"              : ".eot",
    "application/postscript"                : ".ps",
    "application/x-sqlite3"                 : ".sqlite",
    "application/x-nintendo-nes-rom"        : ".nes",
    "application/x-google-chrome-extension" : ".crx",
    "application/vnd.ms-cab-compressed"     : ".cab",
    "application/x-deb"                     : ".deb",
    "application/x-unix-archive"            : ".ar",
    "application/x-compress"                : ".Z",
    "application/x-lzip"                    : ".lz",
}

def decide_extension(content_encoding=None, content_type=None, filename=None):
    """Decide File Extension based on ``content_encoding`` and ``content_type``

    Args:
        content_encoding (str) : The MIME type of the resource or the data.
        content_type (str)     : The Content-Encoding entity header is used to compress the media-type.
        filename (str)         : The filename.

    Returns:
        ext (str): Starts with "."

    Examples:
        >>> from pycharmers.utils import decide_extension
        >>> decide_extension(content_encoding="x-gzip", content_type="application/zip")
        .gz
        >>> decide_extension(content_encoding="image/png", content_type=None)
        .png
        >>> decide_extension(content_encoding=None, content_type="application/pdf")
        .pdf
    """
    ext = CONTENT_ENCODING2EXT.get(content_encoding) or CONTENT_TYPE2EXT.get(content_type) or "." + str(filename).split(".")[-1]
    return ext

def download_file(url, dirname=".", path=None, bar_width=20, verbose=True):
    """Download a file.

    Args:
        url (str)       : File URL.
        dirname (str)   : The directory where downloaded data will be saved.
        path (str)      : path/to/downloaded_file
        bar_width (int) : The width of progress bar.
        verbose (bool)  : Whether print verbose or not.

    Returns:
        path (str) : path/to/downloaded_file
    
    Examples:
        >>> from pycharmers.utils import download_file
        >>> download_file(url="https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml")
        Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
                    * Content-Encoding : None
                    * Content-Length   : (333.404296875, 'MB')
                    * Content-Type     : text/plain; charset=utf-8
                    * Save Destination : ./haarcascade_eye.xml 
        haarcascade_eye.xml	100.0%[####################] 0.1[s] 5.5[GB/s]	eta -0.0[s]
        './haarcascade_eye.xml'
    """    
    try:
        with urllib.request.urlopen(url) as web_file:
            # Get Information from webfile header
            headers = dict(web_file.headers._headers)
        content_encoding     = headers.get("Content-Encoding")
        content_length, unit = readable_bytes(int(headers.get("Content-Length", 0)))
        content_length       = f"{content_length:.1f} [{unit}]"
        content_type         = headers.get("Content-Type")
        fn = url.split("/")[-1]
        if path is None:
            *name, ext = fn.split(".")
            name = ".".join(name)
            guessed_ext = decide_extension(content_encoding, content_type, fn)
            path = os.path.join(dirname, name+guessed_ext)
        if verbose:
            print(*pretty_3quote(f"""
            Download a file from {toBLUE(url)}
            * Content-Encoding : {toGREEN(content_encoding)}
            * Content-Length   : {toGREEN(content_length)}
            * Content-Type     : {toGREEN(content_type)}
            * Save Destination : {toBLUE(path)}"""
            ))
        _, res = urllib.request.urlretrieve(url=url, filename=path, reporthook=progress_reporthook_create(filename=fn, bar_width=bar_width, verbose=verbose))
    except urllib.error.URLError as e:
        if verbose: print(f"{toRED(e)} : url={toBLUE(url)}")
    return path