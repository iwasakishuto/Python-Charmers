# coding: utf-8
def test_Table():
    from pycharmers.utils import Table, toBLUE
    table = Table(enable_colspan=True)
    table.set_cols([1,2,""], colname="id")
    table.set_cols([toBLUE("abc"), "", "de"], color="GREEN")
    table.show()
    # +----+-------+
    # | id | col.2 |
    # +====+=======+
    # |  1 |   [34mabc[0m |
    # +----+       +
    # |  2 |       |
    # +    +-------+
    # |    |    [32mde[0m |
    # +----+-------+

def test_align_text():
    from pycharmers.utils import align_text, toBLUE
    print(align_text("Hello world!", align=">", width=15))
    #    Hello world!
    print(align_text(toBLUE("Hello world!"), align=">", width=15))
    #    [34mHello world![0m

def test_format_spec_create():
    from pycharmers.utils import format_spec_create
    format_spec = format_spec_create(width=10, align="^")
    format_spec("hoge")
    # '   hoge   '
    format_spec = format_spec_create(align="<", fmt=".1%")
    format_spec(1/3)
    # '33.3%'
    format_spec = format_spec_create(align=">", zero_padding=True, fmt="b")
    format_spec(20)
    # '10100'

def test_pretty_3quote():
    from pycharmers.utils import pretty_3quote
    print(*pretty_3quote("""
        When I was 17, I read a quote that went something like: 
        “If you live each day as if it was your last, someday you’ll most certainly be right.”
        It made an impression on me, and since then, for the past 33 years, 
    """))
    # When I was 17, I read a quote that went something like: 
    # “If you live each day as if it was your last, someday you’ll most certainly be right.”
    # It made an impression on me, and since then, for the past 33 years, 

def test_print_dict_tree():
    from pycharmers.utils import print_dict_tree
    print_dict_tree({"a": 0, "b": 1})
    # - a: 0
    # - b: 1
    print_dict_tree({"a": 0, "b": {"b1": 1, "b2": 2}})
    # - a: 0
    # - b: 
    #   * b1: 1
    #   * b2: 2
    print_dict_tree({"a": 0, "b": {"b1": 1, "b2": {"b21": 0, "b22": 1}}, "c": 3})
    # - a: 0
    # - b: 
    #   * b1: 1
    #   * b2: 
    #     # b21: 0
    #     # b22: 1
    # - c: 3

def test_print_func_create():
    from pycharmers.utils import print_func_create
    print_func = print_func_create(width=8, align="^", left_side_bar="[", right_side_bar="]")
    print_func("hoge")
    # [  hoge  ]
    print_func = print_func_create(align="<", left_side_bar="$ ")
    print_func("git clone https://github.com/iwasakishuto/Python-utils.git")
    # $ git clone https://github.com/iwasakishuto/Python-utils.git
    print_func("cd Python-utils")
    # $ cd Python-utils
    print_func("sudo python setup.py install")
    # $ sudo python setup.py install

def test_str2pyexample():
    from pycharmers.utils import str2pyexample
    WINDOW_NAME = "string2python"
    str2pyexample("""
    import cv2
    import numpy as np
    frame = np.zeros(shape=(50, 100, 3), dtype=np.uint8)
    while (True):
        cv2.imshow(WINDOW_NAME, frame)
        if cv2.waitKey(0) == 27: break
    cv2.destroyAllWindows()
    """)
    import cv2
    import numpy as np
    frame = np.zeros(shape=(50, 100, 3), dtype=np.uint8)
    while (True):
        cv2.imshow(WINDOW_NAME, frame)
        if cv2.waitKey(0) == 27: break
    cv2.destroyAllWindows()


def test_strip_invisible():
    from pycharmers.utils import strip_invisible, toBLUE
    strip_invisible("[31mhello[0m")
    # 'hello'
    strip_invisible(toBLUE("hello"))
    # 'hello'
    strip_invisible("hello")
    # 'hello'

def test_tabulate():
    from pycharmers.utils import tabulate
    tabulate([[i*j for i in range(1,4)] for j in range(1,4)])
    # +-------+-------+-------+
    # | col.1 | col.2 | col.3 |
    # +=======+=======+=======+
    # |     1 |     2 |     3 |
    # +-------+-------+-------+
    # |     2 |     4 |     6 |
    # +-------+-------+-------+
    # |     3 |     6 |     9 |
    # +-------+-------+-------+

def test_visible_width():
    from pycharmers.utils import visible_width, toBLUE
    visible_width(toBLUE("hello"))
    # 5
    visible_width("こんにちは")
    # 10
    visible_width("hello 世界。")
    # 12

