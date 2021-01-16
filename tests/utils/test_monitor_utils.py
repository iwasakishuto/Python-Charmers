# coding: utf-8
def test_ProgressMonitor():
    from pycharmers.utils import ProgressMonitor
    max_iter = 100
    monitor = ProgressMonitor(max_iter=max_iter, verbose=1, barname="NAME")
    for it in range(max_iter):
        monitor.report(it, loop=it+1)
    monitor.remove()
    # NAME 100/100[####################]100.00% - 0.010[s]  loop: 100

def test_progress_reporthook_create():
    import urllib
    from pycharmers.utils import progress_reporthook_create
    urllib.request.urlretrieve(url="hoge.zip", filename="hoge.zip", reporthook=progress_reporthook_create(filename="hoge.zip"))
    # hoge.zip	1.5%[--------------------] 21.5[s] 8.0[GB/s]	eta 1415.1[s]

