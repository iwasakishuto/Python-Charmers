# coding: utf-8
import os
import re
import urllib
import requests
from bs4 import BeautifulSoup

from ..utils._path import _makedirs
from ..utils.download_utils import download_file


def url2raw(url):
    """Convert from Github URL to Raw URL.

    Args:
        url (str) : Github URL.

    Examples:
        >>> from pycharmers.utils import pycat, download_file
        >>> from pycharmers.sdk import url2raw
        >>> github_url = "https://github.com/opencv/opencv/blob/master/data/CMakeLists.txt"
        >>> path = download_file(url=github_url, dirname=".")
        >>> pycat(path, head=10)
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
        <link rel="dns-prefetch" href="https://github.githubassets.com">
        # The above file is HTML!!
        # Therefore, convert from Github URL to Raw URL.
        >>> raw_url = url2raw(github_url)
        >>> path = download_file(url=raw_url, dirname=".")
        >>> pycat(path, head=2)
        file(GLOB HAAR_CASCADES haarcascades/*.xml)
        file(GLOB LBP_CASCADES lbpcascades/*.xml)
        # Get the desired data :)    
    """
    return url.replace("://github.com/", "://raw.githubusercontent.com/").replace("/blob/", "/")

def wgit(base_url="", base_dir=".", depth=0):
    """Download only a specific folder or directory from a remote Git repo hosted on GitHub.

    Args:
        base_url (str) : URL for a specific folder or directory from a remote Git repository.
        base_dir (str) : The directory where downloaded data will be saved.
        depth (int)    : Depth of the directory tree.

    Examples:
        >>> from pycharmers.sdk import wgit
        >>> from pycharmers.opencv import PYCHARMERS_OPENCV_DIR
        >>> wgit(base_url="https://github.com/opencv/opencv/tree/master/data", base_dir=PYCHARMERS_OPENCV_DIR)
        /Users/iwasakishuto/.pycharmers/opencv/data is created. 
        /Users/iwasakishuto/.pycharmers/opencv/data/haarcascades is created. 
        Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
                    * Content-Encoding : None
                    * Content-Length   : (333.404296875, 'MB')
                    * Content-Type     : text/plain; charset=utf-8
                    * Save Destination : /Users/iwasakishuto/.pycharmers/opencv/data/haarcascades/haarcascade_eye.xml
        haarcascade_eye.xml	100.0%[####################] 0.1[s] 4.5[GB/s]	eta -0.0[s]
        Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye_tree_eyeglasses.xml
        :
    """
    if depth==0:
        base_dir = os.path.join(base_dir, os.path.basename(base_url))
        _makedirs(name=base_dir)
    soup = BeautifulSoup(markup=requests.get(url=base_url).content, features="lxml")
    # indent = "\t"*depth
    for row in soup.find_all(name="div", class_="py-2", role="row"):
        href = row.find(name="a", class_="js-navigation-open").get("href", "")
        url  = urllib.parse.urljoin(base=base_url, url=href)
        icon_aria_label = row.find(name="svg").get("aria-label")
        if icon_aria_label == "Directory":
            dirname = os.path.join(base_dir, os.path.basename(href))
            _makedirs(name=dirname)
            wgit(base_url=url, base_dir=dirname, depth=depth+1)
        else:
            download_file(url=url2raw(url), dirname=base_dir)