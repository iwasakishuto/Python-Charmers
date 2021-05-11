# coding: utf-8
def test_assign_trbl():
    from pycharmers.utils import assign_trbl
    assign_trbl(data={"margin": [1,2,3,4]}, name="margin")
    # (1, 2, 3, 4)
    assign_trbl(data={"margin": [1,2,3]}, name="margin")
    # (1, 2, 3, 2)
    assign_trbl(data={"margin": [1,2]}, name="margin")
    # (1, 2, 1, 2)
    assign_trbl(data={"margin": 1}, name="margin")
    # (1, 1, 1, 1)
    assign_trbl(data={"margin": 1}, name="padding", default=5)
    # (5, 5, 5, 5)

def test_calc_rectangle_size():
    from pycharmers.utils import calc_rectangle
    calc_rectangle(12, 3)
    # (3, 4)
    calc_rectangle(12, 18)
    # (12, 1)
    calc_rectangle(12, 7)
    # (7, 2)


def test_class2str():
    from pycharmers.utils import class2str
    class2str(str)
    # 'str'
    class2str(tuple)
    # 'tuple'


def test_filenaming():
    import os
    from pycharmers.utils import filenaming
    print(os.listdir())
    # ['Untitled.ipynb', 'Untitled(1).ipynb', 'Untitled(3).ipynb']
    filenaming("Untitled.ipynb")
    # './Untitled(2).ipynb'
    filenaming("Untitled.py")
    # 'Untitled.py'

def test_formatted_enumerator():
    from pycharmers.utils import formatted_enumerator
    gen = formatted_enumerator(["a","b","c"])
    for i,d in gen:
        print(i, d)
    # 1 a
    # 2 i
    # 3 u        

def test_get_create():
    import cv2
    from pycharmers.utils import get_create
    all = PYCHARMERS_BACKGROUND_SUBTRACTOR_CREATORS = {
        "mog" : cv2.createBackgroundSubtractorMOG2,
        "knn" : cv2.createBackgroundSubtractorKNN,
    }
    background_subtractor_create = get_create(corresp_dict=all, class_=[cv2.BackgroundSubtractor], genre="background_subtractor")

def test_get_pyenv():
    from pycharmers.utils import get_pyenv
    get_pyenv(globals())
    # 'Jupyter Notebook'

    # :
    # Execute this function without arguments.

def test_handleKeyError():
    from pycharmers.utils import handleKeyError
    handleKeyError(lst=range(3), val=1)
    handleKeyError(lst=range(3), val=100)
    # KeyError: Please choose the argment val from ['0', '1', '2']. you chose 100
    handleKeyError(lst=range(3), val1=1, val2=2)
    handleKeyError(lst=range(3), val1=1, val2=100)
    # KeyError: Please choose the argment val2 from ['0', '1', '2']. you chose 100

    # e:
    # KeyError: If ``kwargs.values()`` not in the ``lst``

def test_handleTypeError():
    from pycharmers.utils import handleTypeError
    handleTypeError(types=[str], val="foo")
    handleTypeError(types=[str, int], val=1)
    handleTypeError(types=[str, int], val=1.)
    # TypeError: val must be one of ['str', 'int'], not float
    handleTypeError(types=[str], val1="foo", val2="bar")
    handleTypeError(types=[str, int], val1="foo", val2=1.)
    # TypeError: val2 must be one of ['str', 'int'], not float

    # e:
    # TypeError: If the types of ``kwargs.values()`` are none of the ``types``

def test_html2reStructuredText():
    from pycharmers.utils import html2reStructuredText
    html2reStructuredText("<code>CODE</code>")
    # ' ``CODE`` '      
    html2reStructuredText(
        html='<a class="reference internal" href="pycharmers.html">pycharmers package</a>',
        base_url="https://iwasakishuto.github.io/Python-Charmers/"
    )
    # '`pycharmers package <https://iwasakishuto.github.io/Python-Charmers/pycharmers.html>`_'

def test_infer_types():
    from pycharmers.utils import infer_types
    infer_types(1)
    # int
    infer_types(1.1)
    # float
    infer_types("1e3")
    # float
    infer_types("Hello")
    # str

def test_int2ordinal():
    from pycharmers.utils import int2ordinal
    int2ordinal(0)
    # '0th'
    int2ordinal(1)
    # '1st'
    int2ordinal(2)
    # '2nd'
    int2ordinal(3)
    # '3rd'
    int2ordinal(4)
    # '4th'
    int2ordinal(11)
    # '11th'
    int2ordinal(21)
    # '21st'
    int2ordinal(111)
    # '111th'
    int2ordinal(121)
    # '121st'

def test_list2name():
    from pycharmers.utils import list2name
    list2name(lst=["iwasaki", "shuto"], how="camel")
    # 'iwasakiShuto'
    list2name(lst=["iwasaki", "shuto"], how="pascal")
    # 'IwasakiShuto'
    list2name(lst=["iwasaki", "shuto"], how="snake")
    # 'iwasaki_shuto'
    list2name(lst=["iwasaki", "shuto"], how="kebab")
    # 'iwasaki-shuto'

def test_open_new_tab():
    from pycharmers.utils import open_new_tab
    open_new_tab("https://google.com")
    # True
    open_new_tab("sample.html")
    # True

def test_pycat():
    from pycharmers.opencv import SAMPLE_LENA_IMG
    from pycharmers.utils import pycat
    pycat(SAMPLE_LENA_IMG, mode="rb")

def test_pytree():
    from pycharmers.utils import pytree
    from pycharmers.utils._path import REPO_DIR
    pytree(REPO_DIR, pattern="**/*.py", max_level=3)
    # /Users/iwasakishuto/Github/portfolio/Python-Charmers
    # ├── build
    # │   └── lib
    # │       ├── pycharmers
    # │       └── pyutils
    # ├── pycharmers
    # │   ├── __init__.py

def test_readable_bytes():
    from pycharmers.utils import readable_bytes
    size, unit = readable_bytes(1e2)
    print(f"{size:.2f}[{unit}]")
    # 100.00[KB]
    size, unit = readable_bytes(1e5)
    print(f"{size:.2f}[{unit}]")
    # 97.66[MB]
    size, unit = readable_bytes(1e10)
    print(f"{size:.2f}[{unit}]")
    # 9.31[GB]

def test_relative_import():
    import os
    from pycharmers.utils import relative_import
    relative_import(f="..utils", i="LeNet", absfile=os.path.abspath(__file__), name=__name__)

def test_try_wrapper():
    from pycharmers.utils import try_wrapper
    ret = try_wrapper(lambda x,y: x/y, 1, 2, msg_="divide")
    # Succeeded to divide
    ret
    # 0.5
    ret = try_wrapper(lambda x,y: x/y, 1, 0, msg_="divide")
    # [division by zero] Failed to divide
    ret is None
    # True
    ret = try_wrapper(lambda x,y: x/y, 1, 0, ret_=1, msg_="divide")
    ret is None
    # False
    ret
    # 1

