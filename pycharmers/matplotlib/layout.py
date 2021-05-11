# coding: utf-8
import os
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from ..utils.generic_utils import calc_rectangle_size, list_transpose, open_new_tab
from ..utils.templates import render_template
from ..utils._path import PYCHARMERS_HTML_DIR

def FigAxes_create(fig=None, ax=None, figsize=(6,4), projection=None, nplots=1, ncols=1, nrows=1, axis=0, facecolor="white", **kwargs):
    """ Create a figure and a subplot (a set of subplots).

    Args:
        fig (Figure)     : The ``Figure`` instance.
        ax (Axes)        : The ``Axes`` instance.
        figsize (tuple)  : The figure size for ``1`` plot.
        projection (str) : The projection type of the subplot.
        nplots (int)     : Total number of Plots.
        nrows (int)      : The number of rows
        ncols (int)      : The number of columns.
        axis (int)       : ``0`` or ``1`` Direction to arrange axes.
        facecolor (str)  : The background color. (default= ``"white"`` )
        \*\*kwargs         : ``kwargs`` for add_subplot(\*args, \*\*kwargs) method of ``matplotlib.figure.Figure`` instance.

    Returns:
        fig (Figure) : The ``Figure`` instance
        ax (Axes)    : An array of ``Axes`` objects if more than one subplot was created.
    
    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import FigAxes_create
        >>> num_data = 10
        >>> data = range(num_data)
        >>> fig, axes = FigAxes_create(nplots=num_data, ncols=4, figsize=(4,4))
        >>> for x,ax in zip(data,axes):
        ...     ax.scatter(x,x,s=x+1)
        >>> plt.show()
    """
    facecolor = kwargs.pop("facecolor", facecolor)
    if ax is None:
        if fig is None:
            ncols, nrows, total_figsize = measure_canvas(nplots=nplots, ncols=ncols, figsize=figsize)
            fig = plt.figure(figsize=total_figsize, facecolor=facecolor)
        elif ncols*nrows<nplots:
            ncols, nrows = calc_rectangle_size(area=nplots, w=ncols)
        ax = [fig.add_subplot(nrows, ncols, i+1, projection=projection, **kwargs) for i in range(nplots)]
        if axis==1:
            ax = list_transpose(lst=ax, width=ncols)
    elif not isinstance(ax, list):
        ax = [ax]
    return (fig, ax)

def set_ax_info(ax, **kwargs):
    """Set Axes information

    Args:
        ax (Axes) : The ``Axes`` instance.
        kwargs    : ``key`` indicate the method which is start with ``set_``, and the method takes arguments (``val``) according to the type of ``val``

    Returns:
        ax (Axes) : The ``Axes`` instance.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import set_ax_info
        >>> fig, ax = plt.subplots(nplots=1)[0]
        >>> ax = set_ax_info(ax, aspect=5, title="Title", xlabel="Xlabel", ylabel="Ylabel", yticks={"ticks":[]})
        >>> ax.scatter(1,1)
        >>> plt.show() 
    """
    for k,v in kwargs.items():
        method = ax.__getattribute__(f"set_{k}")
        if isinstance(v, str) and v=="_void":
            method()
        elif isinstance(v, dict):
            method(**v)
        elif isinstance(v, tuple):
            method(*v)
        elif isinstance(v, list) and len(v)==2 and (isinstance(v[0], tuple) and isinstance(v[1], dict)):
            args, kwargs = v
            method(*args, **kwargs)
        else:
            method(v)
    return ax

def clear_grid(ax, pos=["x","y"]):
    """Clear a grid

    Args:
        ax (Axes)  : The ``Axes`` instance.
        pos (list) : Positions to clean a grid

    Examples:
        >>> from pyutils.matplotlib import clear_grid, FigAxes_create
        >>> fig,ax = FigAxes_create(nplots=1)[0]
        >>> ax = clear_grid(ax=ax, pos=["x", "y"])
        >>> ax = clear_grid(ax=ax, pos=list("ltrb"))
    """
    if isinstance(pos, str):
        pos = [pos]
    for p in pos:
        if p in ["x", "b", "bottom"]:
            ax.tick_params(labelbottom=False, bottom=False)
            ax.set_xticklabels([])
        elif p in ["y", "l", "left"]:
            ax.tick_params(labelleft=False, left=False)
            ax.set_yticklabels([])
        elif p in ["r", "right"]:
            ax.tick_params(labelright=False, right=False)
        elif p in ["t", "top"]:
            ax.tick_params(labeltop=False, top=False)
        elif p == "all":
            ax.set_axis_off()
    return ax

def measure_canvas(nplots, ncols=2, figsize=(6,4)):
    """ Measure Canvas size.

    Args:
        nplots (int)    : Total number of figures.
        ncols (int)     : The number of columns.
        figsize (tuple) : The figure size for ``1`` plot.

    Returns:
        ncols (int)           : The number of columns.
        nrows (int)           : The number of rows.
        total_figsize (tuple) : The total figure size.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import measure_canvas
        >>> num_data = 10
        >>> data = range(num_data)
        >>> ncols, nrows, total_figsize = measure_canvas(nplots=num_data, ncols=4, figsize=(4,4))
        >>> fig, axes = plt.subplots(nrows=nrows, ncols=ncols, sharex="all", sharey="all", figsize=total_figsize)
        >>> plot_all = False
        >>> for i,ax_row in enumerate(axes):
        ...     for j,ax in enumerate(ax_row):
        ...         idx = i*ncols+j
        ...         if idx>=num_data:
        ...             plot_all = True
        ...         if plot_all:
        ...             fig.delaxes(ax)            
        ...         else:            
        ...             x = data[idx]+1
        ...             ax.scatter(x,x,s=x*10)
        >>> plt.show()
    """
    ncols, nrows = calc_rectangle_size(area=nplots, w=ncols)
    w, h = figsize
    total_figsize = (w*ncols, h*nrows)
    return (ncols, nrows, total_figsize)

def show_all_fonts():
    """Show all fonts available in ``matplotlib`` ."""
    fn = "matplotlib.font_manager.fontManager.ttflist.html"
    path = os.path.join(PYCHARMERS_HTML_DIR, fn)
    render_template(
        template_name_or_string="fonts.html", 
        context={"fonts": sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))},
        path=path
    )
    open_new_tab(path)

def mpljapanize(font_family="IPAMincho"):
    """Make matplotlib compatible with Japanese"""
    from matplotlib import rcParams
    rcParams["font.family"] = font_family