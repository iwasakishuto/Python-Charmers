# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt

from .layout import FigAxes_create, set_ax_info
from ..utils.numpy_utils import confusion_matrix, take_centers

def plot_hist(data, bins=None, ax=None, roffset=0.01, hist_color="blue", anno_color="green"):
    """Plot Histogram

    Args:
        data (array)     : Array-like sample data.
        bins (int)       : Defines the number of equal-width bins in the range.
        ax (AxesSubplot) : The ``Axes`` instance.
        roffset (float)  : Offset from histogram to annotation text.
        hist_color (str) : The histogram color.
        anno_color (str) : The annotation text color.

    Example:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_hist
        >>> data = np.random.normal(size=1000)
        >>> ax = plot_hist(data)
        >>> plt.show()
    """
    fig, ax = FigAxes_create(ax=ax)
    Y, bins, _ = ax.hist(data, bins=bins, color=hist_color)
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
        >>> num_data = 1000
        >>> rnd = np.random.RandomState(123)
        >>> labels = rnd.randint(low=0, high=4, size=num_data)
        >>> data   = rnd.normal(size=num_data) + labels*0.25
        >>> ax = plot_cumulative_ratio(data, labels=labels, bar=True)
        >>> ax.legend()
        >>> plt.show()
    """
    num_data = len(data)
    _, bin_edges = np.histogram(a=data, bins=bins)
    X = take_centers(bin_edges)
    if reverse: X = X[::-1]

    #=== Calcurate each group's plot information. ===
    if labels is None: labels = np.zeros_like(data)
    hists = np.zeros(shape=(1,bins))
    groups = np.unique(labels)
    for g in groups:
        hist, _ = np.histogram(a=data[labels==g], bins=bins)
        if reverse: hist = hist[::-1]
        # Memorize the "n" for each label.
        hists = np.r_[hists, np.cumsum(hist).reshape(1,-1)]

    # Plot
    fig, ax = FigAxes_create(ax=ax)
    hists /= num_data
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

def plot_classification_performance(cm=None, y_true=None, y_pred=None, cmap="RdBu", answer_label="answer", predict_label="predict"):
    """Plot model's classification performance.

    Args:
        cm (array)          : Confusion matrix whose i-th row and j-th column entry indicates the number of samples with true label being i-th class and prediced label being j-th class.
        y_true (array)      : Ground truth (correct) target values.
        y_pred (array)      : Estimated targets as returned by a classifier.
        cmap (str)          : The name of a color map known to ``matplotlib``
        answer_label (str)  : The label name on the correct answer side.
        predict_label (str) : The label name on the prediction side.

    Examples:
        >>> import numpy as np
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import plot_classification_performance
        >>> rnd = np.random.RandomState(123)
        >>> y_true = rnd.randint(low=0, high=4, size=100)
        >>> y_pred = rnd.randint(low=0, high=4, size=100)
        >>> plot_classification_performance(y_true=y_true, y_pred=y_pred)
        >>> plt.show()
    """
    if cm is None:
        cm = confusion_matrix(y_true=y_true, y_pred=y_pred)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.matshow(cm, cmap=cmap, alpha=0.3)
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(x=j, y=i, s=cm[i, j], va="center", ha="center")
    ax = set_ax_info(ax, title={"label": predict_label, "fontsize": 16}, ylabel={"ylabel":answer_label, "fontsize": 16})
    return ax