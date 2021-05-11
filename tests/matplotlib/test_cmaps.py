# coding: utf-8
def test_color_dict_create():
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import color_dict_create
    color_dict_create(keys=["a","b","c"], cmap="jet")
    # {
    #     'b': (0.0, 0.0, 0.5, 1.0),
    #     'c': (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
    #     'a': (0.5, 0.0, 0.0, 1.0)
    # }
    color_dict_create(keys=3, cmap="jet")
    # {
    #     0: (0.0, 0.0, 0.5, 1.0),
    #     1: (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
    #     2: (0.5, 0.0, 0.0, 1.0)
    # }
    color_dict_create(keys=["a","b","c"], cmap=plt.get_cmap("jet"))
    # {
    #     'b': (0.0, 0.0, 0.5, 1.0),
    #     'c': (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
    #     'a': (0.5, 0.0, 0.0, 1.0)
    # }

