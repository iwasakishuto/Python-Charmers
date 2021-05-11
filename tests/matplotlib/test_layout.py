# coding: utf-8
def test_FigAxes_create():
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import FigAxes_create
    num_data = 10
    data = range(num_data)
    fig, axes = FigAxes_create(nplots=num_data, ncols=4, figsize=(4,4))
    for x,ax in zip(data,axes):
        ax.scatter(x,x,s=x+1)
    plt.show()

def test_clear_grid():
    from pyutils.matplotlib import clear_grid, FigAxes_create
    fig,ax = FigAxes_create(nplots=1)[0]
    ax = clear_grid(ax=ax, pos=["x", "y"])
    ax = clear_grid(ax=ax, pos=list("ltrb"))

def test_measure_canvas():
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import measure_canvas
    num_data = 10
    data = range(num_data)
    ncols, nrows, total_figsize = measure_canvas(nplots=num_data, ncols=4, figsize=(4,4))
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex="all", sharey="all", figsize=total_figsize)
    plot_all = False
    for i,ax_row in enumerate(axes):
        for j,ax in enumerate(ax_row):
            idx = i*ncols+j
            if idx>=num_data:
                plot_all = True
            if plot_all:
                fig.delaxes(ax)            
            else:            
                x = data[idx]+1
                ax.scatter(x,x,s=x*10)
    plt.show()

def test_set_ax_info():
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import set_ax_info
    fig, ax = plt.subplots(nplots=1)[0]
    ax = set_ax_info(ax, aspect=5, title="Title", xlabel="Xlabel", ylabel="Ylabel", yticks={"ticks":[]})
    ax.scatter(1,1)
    plt.show() 

