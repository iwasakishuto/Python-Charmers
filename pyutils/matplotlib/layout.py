# coding: utf-8
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from ..utils.generic_utils import calc_rectangle_size

def FigAxes_create(fig=None, ax=None, figsize=(6,4), projection=None, nfigs=1, ncols=1, nrows=1, **kwargs):
    """ Create a figure and a subplot (a set of subplots).

    Args:
        fig (Figure)     : The ``Figure`` instance.
        ax (Axes)        : The ``Axes`` instance.
        figsize (tuple)  : The figure size for ``1`` plot.
        projection (str) : The projection type of the subplot.
        nfigs (int)      : Total number of figures.
        nrows (int)      : The number of rows
        ncols (int)      : The number of columns.
        **kwargs         : ``kwargs`` for add_subplot(*args, **kwargs) method of ``matplotlib.figure.Figure`` instance.

    Returns:
        fig (Figure) : The ``Figure`` instance
        ax (Axes)    : ``ax`` can be either a single ``Axes`` object or an array of ``Axes`` objects if more than one subplot was created.
    
    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pyutils.matplotlib import FigAxes_create
        >>> num_data = 10
        >>> data = range(num_data)
        >>> fig, axes = FigAxes_create(nfigs=num_data, ncols=4, figsize=(4,4))
        >>> for x,ax in zip(data,axes):
        ...     ax.scatter(x,x,s=x+1)
        >>> plt.show()
    """
    if ax is None:
        if fig is None:
            ncols, nrows, total_figsize = measure_canvas(nfigs=nfigs, ncols=ncols, figsize=figsize)
            fig = plt.figure(figsize=total_figsize)
        ax = [fig.add_subplot(nrows, ncols, i+1, projection=projection, **kwargs) for i in range(nfigs)]
        if nfigs==1: ax = ax[0]
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
        >>> from pyutils.matplotlib import set_ax_info
        >>> fig, ax = plt.subplots()
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

def clear_grid(ax, axis=["x","y"]):
    if isinstance(axis, str):
        axis = [axis]
    for axi in axis:
        if axi == "x":
            ax.tick_params(labelbottom=False, bottom=False)
            ax.set_xticklabels([])
        elif axi == "y":
            ax.tick_params(labelleft=False, left=False)
            ax.set_yticklabels([])
        elif axi == "all":
            ax.set_axis_off()
    return ax

def measure_canvas(nfigs, ncols=2, figsize=(6,4)):
    """ Measure Canvas size.

    Args:
        nfigs (int)     : Total number of figures.
        ncols (int)     : The number of columns.
        figsize (tuple) : The figure size for ``1`` plot.

    Returns:
        ncols (int)           : The number of columns.
        nrows (int)           : The number of rows.
        total_figsize (tuple) : The total figure size.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pyutils.matplotlib import measure_canvas
        >>> num_data = 10
        >>> data = range(num_data)
        >>> ncols, nrows, total_figsize = measure_canvas(nfigs=num_data, ncols=4, figsize=(4,4))
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
    ncols, nrows = calc_rectangle_size(area=nfigs, w=ncols)
    w, h = figsize
    total_figsize = (w*ncols, h*nrows)
    return (ncols, nrows, total_figsize)