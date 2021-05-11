# coding: utf-8
def test_decide_extension():
    from pycharmers.utils import decide_extension
    decide_extension(content_encoding="x-gzip", content_type="application/zip")
    
    decide_extension(content_encoding="image/png", content_type=None)
    
    decide_extension(content_encoding=None, content_type="application/pdf")
    

def test_download_file():
    from pycharmers.utils import download_file
    download_file(url="https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml")
    # Download a file from https://raw.githubusercontent.com/opencv/opencv/master/data/haarcascades/haarcascade_eye.xml
    #             * Content-Encoding : None
    #             * Content-Length   : (333.404296875, 'MB')
    #             * Content-Type     : text/plain; charset=utf-8
    #             * Save Destination : ./haarcascade_eye.xml 
    # haarcascade_eye.xml	100.0%[####################] 0.1[s] 5.5[GB/s]	eta -0.0[s]
    # './haarcascade_eye.xml'

