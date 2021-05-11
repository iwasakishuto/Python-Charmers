# coding: utf-8
import numbers
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection

from .layout import FigAxes_create, set_ax_info, measure_canvas
from .cmaps import color_dict_create
from ..utils.numpy_utils import confusion_matrix, take_centers
from ..utils.generic_utils import handleKeyError

def plot_hist(data, bins=None, ax=None, roffset=0.01, rwidth=0.95, hist_color=None, anno_color="green"):
    """Plot Histogram

    Args:
        data (array)     : Array-like sample data.
        bins (int)       : Defines the number of equal-width bins in the range.
        ax (AxesSubplot) : The ``Axes`` instance.
        roffset (float)  : Offset from histogram to annotation text.
        rwidth (float)   : The relative width of the bars as a fraction of the bin width.  If ``None``, automatically compute the width.
        hist_color (str) : The histogram color.
        anno_color (str) : The annotation text color.

    Example:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_hist
        >>> fig, ax = plt.subplots()
        >>> data = np.random.RandomState(123).normal(size=1000)
        >>> ax = plot_hist(data, ax=ax, rwidth=0.95)
        >>> fig.savefig("matplotlib.plot2d.plot_hist.jpg")

    +-----------------------------------------------------------+
    |                         Results                           |
    +===========================================================+
    | .. image:: _images/matplotlib.plot2d.plot_hist.jpg        |
    +-----------------------------------------------------------+
    """
    ax = FigAxes_create(ax=ax)[1][0]
    Y, bins, _ = ax.hist(data, bins=bins, color=hist_color, rwidth=rwidth)
    X = take_centers(bins)
    offset_real = np.max(Y) * roffset
    for x, y in zip(X, Y):
        ax.text(x, y+offset_real, str(int(y)), horizontalalignment="center", color=anno_color, weight="heavy")
    return ax

def plot_cumulative_ratio(data, labels=None, bins=10, width=0.8, reverse=False, ax=None, bar=False, cmap=None):
    """Plot Cumulative Ration (bar graph / line graph)

    Args:
        data (array)     : Array-like sample data.
        labels (array)   : Array-like labels.
        bins (int)       : Defines the number of equal-width bins in the range.
        reverse (bool)   : Whether plot Reverse cumulative distribution curve or not.
        ax (AxesSubplot) : The ``Axes`` instance.
        bar (bool)       : Whether plot as bar or graph.
        cmap (str)       : The name of a color map known to ``matplotlib``

    Example:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_cumulative_ratio
        >>> ndata = 1000
        >>> rnd = np.random.RandomState(123)
        >>> labels = rnd.randint(low=0, high=4, size=ndata)
        >>> data   = rnd.normal(size=ndata) + labels*0.25
        >>> fig, ax = plt.subplots()
        >>> plot_cumulative_ratio(data, ax=ax, labels=labels, bar=True)
        >>> ax.legend()
        >>> fig.savefig("matplotlib.plot2d.plot_cumulative_ratio.jpg")

    +-----------------------------------------------------------------------+
    |                                     Results                           |
    +=======================================================================+
    | .. image:: _images/matplotlib.plot2d.plot_cumulative_ratio.jpg        |
    +-----------------------------------------------------------------------+

    """
    ndata = len(data)
    _, bin_edges = np.histogram(a=data, bins=bins)
    X = take_centers(bin_edges)
    if reverse: X = X[::-1]

    #=== Calcurate each group"s plot information. ===
    if labels is None: labels = np.zeros_like(data)
    hists = np.zeros(shape=(1,bins))
    groups = np.unique(labels)
    for g in groups:
        hist, _ = np.histogram(a=data[labels==g], bins=bins)
        if reverse: hist = hist[::-1]
        # Memorize the "n" for each label.
        hists = np.r_[hists, np.cumsum(hist).reshape(1,-1)]

    # Plot
    ax = FigAxes_create(ax=ax)[1][0]
    hists /= ndata
    bottoms = np.cumsum(hists, axis=0)
    color_arr = plt.get_cmap(name=cmap, lut=len(groups)).colors
    width = (X[1] - X[0])*width
    Y_past = 0
    for i,(Y,g) in enumerate(zip(hists[1:], groups)):
        if bar:
            ax.bar(X, Y, bottom=bottoms[i], width=width, label=g, align="center", color=color_arr[i])
        else:
            Y_curt = Y+bottoms[i]
            ax.plot(X, Y_curt, label=g, color=color_arr[i], marker="o")
            ax.fill_between(X, Y_past, Y_curt, color=color_arr[i], alpha=0.3)
            Y_past = Y_curt
    return ax

def plot_classification_performance(cm=None, y_true=None, y_pred=None, cmap="RdBu", answer_label="answer", predict_label="predict", ax=None):
    """Plot model"s classification performance.

    Args:
        cm (array)          : Confusion matrix whose i-th row and j-th column entry indicates the number of samples with true label being i-th class and prediced label being j-th class.
        y_true (array)      : Ground truth (correct) target values.
        y_pred (array)      : Estimated targets as returned by a classifier.
        cmap (str)          : The name of a color map known to ``matplotlib``
        ax (AxesSubplot)    : The ``Axes`` instance.
        answer_label (str)  : The label name on the correct answer side.
        predict_label (str) : The label name on the prediction side.

    Returns:
        axes (Axes) : An array of ``Axes`` objects if more than one subplot was created.

    Examples:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_classification_performance
        >>> fig, ax = plt.subplots(figsize=(5,5))
        >>> rnd = np.random.RandomState(123)
        >>> y_true = rnd.randint(low=0, high=4, size=100)
        >>> y_pred = rnd.randint(low=0, high=4, size=100)
        >>> plot_classification_performance(y_true=y_true, y_pred=y_pred, ax=ax)
        >>> fig.savefig("matplotlib.plot2d.plot_classification_performance.jpg")

    +---------------------------------------------------------------------------------+
    |                                     Results                                     |
    +=================================================================================+
    | .. image:: _images/matplotlib.plot2d.plot_classification_performance.jpg        |
    +---------------------------------------------------------------------------------+
    """
    if cm is None:
        cm = confusion_matrix(y_true=y_true, y_pred=y_pred)
    ax = FigAxes_create(ax=ax, figsize=(5,5))[1][0]
    ax.matshow(cm, cmap=cmap, alpha=0.3)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(x=j, y=i, s=cm[i, j], va="center", ha="center")
    ax = set_ax_info(ax, title={"label": predict_label, "fontsize": 16}, ylabel={"ylabel":answer_label, "fontsize": 16})
    return ax

def plot_lines(data, ax=None, transpose=False, margin=0.5, label=None, linewidth=None, linestyle=None, color=None, marker=None, **kwargs):
    """Plot lines.

    Args:
        data (array)     : Array-like sample data.
        ax (AxesSubplot) : The ``Axes`` instance.
        transpose (bool) : Whether lines are horizontal or vertical.
        margin (float)   : Whether plot as bar or graph.
        label (str)      : The label for line"s" data.
        kwargs (dict)    : The key word arguments for ``matplotlib.lines.Line2D``, ``linewidth`` , ``linestyle``, ``color (str)``, ``marker``

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import set_ax_info, plot_lines
        >>> #=== Data ===
        >>> names = ["A", "B", "C", "D", "E", "F", "G"]
        >>> dates = ["early-Jan.","mid-Jan.","late-Jan.","early-Feb.","mid-Feb.","late-Feb.","early-Mar.","mid-Mar.","late-Mar."]
        >>> month_colors = ["#e30013", "#4b73b6", "#f09eb0"]
        >>> schedule_hope = [None, None, 4, 6, 2, 0, 3]
        >>> schedule_inconvenient = [[], [2], [1, 2, 3], [0, 1, 2, 5, 7, 8], [1, 3, 4, 5], [1, 2, 5], [0, 5, 6]]
        >>> num_names = len(names)
        >>> num_dates = len(dates)
        >>> #=== Plot ===
        >>> fig, ax = plt.subplots(figsize=(12,8), dpi=80, facecolor="white")
        >>> ax = plot_lines(data=schedule_inconvenient, ax=ax, transpose=True, color="black", label="Inconvenient")
        >>> ax.scatter(x=schedule_hope, y=[i for i in range(len(schedule_hope))], color="red", s=100, marker="*", label="Hope")
        >>> for i,color in enumerate(month_colors):
        ...     ax.fill((i*3-0.5,i*3-0.5,(i+1)*3-0.5,(i+1)*3-0.5), (num_names,0,0,num_names), color=color, alpha=0.1, label=dates[i*3].split("-")[-1]) 
        >>> #=== Decoration ===
        >>> ax = set_ax_info(ax, **{
        ...     "xticks":      {"ticks" : [i for i in range(num_dates)]},
        ...     "xticklabels": {"labels": dates, "fontsize":16},
        ...     "yticks":      {"ticks" : [i for i in range(num_names)]},
        ...     "yticklabels": {"labels": names, "fontsize":16},
        ...     "title":       {"label": "Results of Schedule Adjustment", "fontsize":20},
        >>> })
        >>> ax.legend()
        >>> plt.tight_layout()
        >>> fig.savefig("matplotlib.plot2d.plot_lines.jpg")

    +------------------------------------------------------------+
    |                           Results                          |
    +============================================================+
    | .. image:: _images/matplotlib.plot2d.plot_lines.jpg        |
    +------------------------------------------------------------+
   
    """
    def newline(x,y,ax,label=None):
        xdata = [x,x]; ydata = [y,y]
        if transpose:
            xdata = [x-margin,x+margin]
        else:
            ydata = [y-margin,y+margin]
        ax.add_line(mlines.Line2D(xdata=xdata, ydata=ydata, linewidth=linewidth, linestyle=linestyle, color=color, marker=marker, label=label, **kwargs))
        return ax
    
    ax = FigAxes_create(ax=ax)[1][0]
    for i,ith_data in enumerate(data):
        if isinstance(ith_data, numbers.Number): 
            ith_data = [ith_data]
        i_=i
        for e in ith_data:
            if transpose:
                e,i = (i_,e)                
            ax = newline(x=i, y=e, ax=ax, label=None)
    ax = newline(x=i, y=e, ax=ax, label=label)
    return ax

def plot_radar_charts(data, varlabels=[], colors=[], datalabels=[], plottitles=[], frame="Circle", radii=[0.0,0.2,0.4,0.6,0.8,1.0], title="", cmap="jet", ncols=1, fig=None, ax=None, figsize=(4,4)):
    """Plot radar charts.

    Args:
        data (np.ndarray)              : Array-like sample data. shape=( ``nplots``, ``ndata``, ``nvars`` ) 
        varlabels (list)               : Array-like labels of varnames. ( ``len(varlabels)==nvars`` )
        colors (list)                  : Colors for each variables. ``len(colors)==ndata``
        datalabels (list)              : Array-like labels of data. ( ``len(datalabels)==ndata`` )
        plottitles (list)              : Array-like labels of plot titles. ( ``len(plottitles)==nplots`` )
        frame (str)                    : Shape of frame surrounding axes. ( ``"Circle"``, or ``"polygon"`` )
        radii (list)                   : The radii for the radial gridlines. (default= ``[0.2,0.4,0.6,0.8]`` )
        title (str)                    : Figure title.
        cmap (str / matplotlib.colors) : Color map. 
        ncols (int)                    : The number of columns.
        fig (Figure)                   : The ``Figure`` instance.
        ax (Axes)                      : The ``Axes`` instance.
        figsize (tuple)                : The figure size for ``1`` plot.

    Examples:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_radar_charts, mpljapanize
        >>> data = np.random.RandomState(123).uniform(low=0.3, high=1.0, size=(2,3,6))
        >>> varlabels  = ["Hit Points", "Attack", "Defense", "Special Attack", "Special Defense", "Speed"] 
        >>> datalabels = ["Evo.1", "Evo.2", "Evo.3"]
        >>> plottitles = ["Ruby", "Sapphire"]
        >>> fig = plt.figure(figsize=(12,6))
        >>> fig.text(x=0.5, y=0.965, s="Stats", horizontalalignment="center", color="black", weight="bold", size="large")
        >>> axes = plot_radar_charts(data=data, varlabels=varlabels, datalabels=datalabels, plottitles=plottitles, cmap="jet", fig=fig, ncols=2)
        >>> fig.tight_layout()
        >>> fig.savefig("matplotlib.plot2d.plot_radar_charts.jpg")        

    +-----------+--------------------------------------------------------------------+
    |                                 Results                                        |
    +===========+====================================================================+
    | ``frame`` |                                                             figure |
    +-----------+--------------------------------------------------------------------+
    |    Circle |  .. image:: _images/matplotlib.plot2d.plot_radar_charts-Circle.jpg |
    +-----------+--------------------------------------------------------------------+
    |   polygon | .. image:: _images/matplotlib.plot2d.plot_radar_charts-polygon.jpg |
    +-----------+--------------------------------------------------------------------+

    """
    if data.ndim==2:
        data = np.expand_dims(data, axis=0)
    nplots, ndata, nvars = data.shape
    if len(varlabels)!=nvars:
        varlabels = [f"var.{i+1:>0{len(str(nvars))}}" for i in range(nvars)]
    if len(colors)!=ndata:
        colors = color_dict_create(keys=ndata, cmap=cmap).values()
    if len(datalabels)!=ndata:
        datalabels = [f"Factor.{i+1:>0{len(str(ndata))}}" for i in range(ndata)]
    if len(plottitles)!=nplots:
        plottitles = [""]*nplots
    theta = np.linspace(start=0, stop=2*np.pi, num=nvars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = "radar"
        RESOLUTION = 1 # use 1 line segment to connect specified points
        SUPPORTED_FRAMES = ["Circle", "polygon"]

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            line.set_data(np.append(x, x[0]), np.append(y, y[0]))

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'Circle':
                from matplotlib.patches import Circle
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                from matplotlib.patches import RegularPolygon
                return RegularPolygon((0.5, 0.5), nvars, radius=.5, edgecolor="k")

        def _gen_axes_spines(self):
            if frame == 'Circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                from matplotlib.path import Path
                from matplotlib.spines import Spine
                from matplotlib.transforms import Affine2D
                spine = Spine(axes=self, spine_type='circle', path=Path.unit_regular_polygon(nvars))
                # unit_regular_polygon gives a polygon of radius 1 centered at (0, 0) but we want a polygon of radius 0.5 centered at (0.5, 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5) + self.transAxes)
                return {'polar': spine}

    handleKeyError(lst=RadarAxes.SUPPORTED_FRAMES, frame=frame)
    register_projection(RadarAxes)

    fig, axes = FigAxes_create(fig=fig, ax=ax, figsize=figsize, projection="radar", nplots=nplots, ncols=ncols)
    for ith_ax,ith_data,ith_title in zip(axes, data, plottitles):
        set_ax_info(ith_ax, **{
            "rlim" : dict(bottom=min(radii), top=max(radii)),
            "rgrids" : dict(radii=radii),
            "title" : dict(label=ith_title, weight="bold", size="medium", position=(0.5, 1.1), horizontalalignment="center", verticalalignment="center"),
            "varlabels" : dict(labels=varlabels),
        })
        for d, color in zip(ith_data, colors):
            ith_ax.plot(theta, d, color=color)
            ith_ax.fill(theta, d, facecolor=color, alpha=0.25)
    axes[0].legend(datalabels, loc=(0.9, .95), labelspacing=0.1, fontsize='small')
    return axes