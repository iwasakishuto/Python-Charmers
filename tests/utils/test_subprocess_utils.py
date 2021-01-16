# coding: utf-8
def test_get_monitor_size():
    from pycharmers.utils import get_monitor_size
    width, height = get_monitor_size()
    print(f"width  : {width}")
    # width  : 1920
    print(f"height : {height}")
    # height : 1958

def test_run_and_capture():
    import os
    from pycharmers.utils import run_and_capture
    os.getcwd() == run_and_capture("pwd")
    # True

