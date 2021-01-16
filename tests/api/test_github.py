# coding: utf-8
def test_url2raw():
    from pycharmers.utils import pycat, download_file
    from pycharmers.api import url2raw
    github_url = "https://github.com/opencv/opencv/blob/master/data/CMakeLists.txt"
    path = download_file(url=github_url, dirname=".")
    pycat(path, head=10)
    # <!DOCTYPE html>
    # <html lang="en">
    # <head>
    #     <meta charset="utf-8">
    # <link rel="dns-prefetch" href="https://github.githubassets.com">
    # # The above file is HTML!!
    # # Therefore, convert from Github URL to Raw URL.
    raw_url = url2raw(github_url)
    path = download_file(url=raw_url, dirname=".")
    pycat(path, head=2)
    # file(GLOB HAAR_CASCADES haarcascades/*.xml)
    # file(GLOB LBP_CASCADES lbpcascades/*.xml)
    # # Get the desired data :)    

def test_wgit():
    from pycharmers.api import wgit
    from pycharmers.opencv import PYCHARMERS_OPENCV_DIR
    wgit(base_url="https://github.com/opencv/opencv/tree/master/data", base_dir=PYCHARMERS_OPENCV_DIR)
    # /Users/iwasakishuto/.pycharmers/opencv/data is created. 
    # /Users/iwasakishuto/.pycharmers/opencv/data/haarcascades is created. 
    # Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
    #             * Content-Encoding : None
    #             * Content-Length   : (333.404296875, 'MB')
    #             * Content-Type     : text/plain; charset=utf-8
    #             * Save Destination : /Users/iwasakishuto/.pycharmers/opencv/data/haarcascades/haarcascade_eye.xml
    # haarcascade_eye.xml	100.0%[####################] 0.1[s] 4.5[GB/s]	eta -0.0[s]
    # Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye_tree_eyeglasses.xml
    # :

