# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from .layout import fig_ax_handler_2D
from ..utils.numpy_utils import confusion_matrix, take_centers

def plot_hist(data, bins=None, ax=None, roffset=0.01, hist_color="blue", text_color="green"):
    """Plot Histogram

    Args:
        data (array)     : 
        bins (int)       : 
        ax (AxesSubplot) : 
        roffset (float)  :
        hist_color (str) :
        text_color (str) :

    Example:
        >>> data = np.random.normal(size=1000)
        >>> ax = plot_hist(data)
        >>> plt.show()
    """
    fig, ax = fig_ax_handler_2D(ax=ax)
    n, bins, a = ax.hist(data, bins=bins, color=hist_color)
    xs = take_centers(bins)
    offset_real = max(n) * roffset
    for x, y in zip(xs, n):
        ax.text(x, y+offset_real, str(int(y)), horizontalalignment="center", color=text_color, weight="heavy")
    return ax

def plot_cumulative_ratio(data, labels=None, bins=10, width=0.8, reverse=False, ax=None, bar=False):
    """Plot Cumulative Ration (bar graph / line graph)

    Args:
        data (array)     : 
        labels (array)   : 
        bins (int)       : 
        reverse (bool)   : 
        ax (AxesSubplot) : 
        bar (bool)       : 

    Example:
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
    fig, ax = fig_ax_handler_2D(ax=ax)
    hists /= num_data # Change number to ratio.
    bottoms = np.cumsum(hists, axis=0)
    cmap = plt.get_cmap("Accent", len(groups)).colors
    width = (X[1] - X[0])*width
    Y_past = 0
    for i,(Y,g) in enumerate(zip(hists[1:], groups)):
        if bar:
            ax.bar(X, Y, bottom=bottoms[i], width=width, label=g, align="center", color=cmap[i])
        else:
            Y_curt = Y+bottoms[i]
            ax.plot(X, Y_curt, label=g, color=cmap[i], marker="o")
            ax.fill_between(X, Y_past, Y_curt, color=cmap[i], alpha=0.3)
            Y_past = Y_curt
    return ax

def plot_model_cm(answer, predict, cmap=plt.cm.RdBu, answer_label="answer", predict_label="predict"):
    cm = confusion_matrix(answer, predict)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.matshow(confmat, cmap=cmap, alpha=0.3)
    for i in range(confmat.shape[0]):
        for j in range(confmat.shape[1]):
            ax.text(x=j, y=i, s=confmat[i, j], va='center', ha='center')
    ax.set_title(predict_label)
    ax.set_ylabel(answer_label)
    return ax

def plot_TF_cm_2Dcond(result, fig=None, ax=None, vmin=0, vmax=1, cmap=plt.cm.RdBu, is_colorbar=False):
    """Plot the true/false value in 2 variable conditions.

    Args:
        result: (ndarray) shape=(N, M, 2)
                   - N: The number of types of the condition 1.
                   - M: The number of types of the condition 2.
                   - 2: True / False vals.
    """
    N,M,_ = result.shape
    prob_cm = np.array([[result[i][j][0]/(sum(result[i][j])+1e-16) for j in range(M)] for i in range(N)])

    if (fig==None) or (ax==None):
        fig, ax = plt.subplots(figsize=(5, 5))
    cax = ax.matshow(prob_cm, cmap=cmap, alpha=0.3, vmin=vmin, vmax=vmax)
    if is_colorbar: fig.colorbar(cax)

    for i in range(N):
        for j in range(M):
            text = f"True:  {result[i][j][0]}\nFalse: {result[i][j][1]}\nProb:  {100*prob_cm[i][j]:.3f}%"
            ax.text(x=j, y=i, s=text, va='center', ha='center')
    return ax

def clear_grid(ax, x=True, y=True):
    if row:
        ax.tick_params(labelbottom=False, bottom=False)
        ax.set_xticklabels([])
    if col:
        ax.tick_params(labelleft=False, left=False)
        ax.set_yticklabels([])
    return ax