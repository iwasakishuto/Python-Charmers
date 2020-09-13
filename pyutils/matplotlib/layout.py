# coding: utf-8
import matplotlib.pyplot as plt

from ..utils import calc_rectangle_size

def fig_ax_handler_2D(fig=None, ax=None, figsize=(6,4)):
    if ax is None:
        if fig is None:
            fig = plt.figure(figsize=figsize)
        ax = fig.add_subplot()
    return (fig, ax)

def fig_ax_handler_3D(fig=None, ax=None, figsize=(6,4)):
    if ax is None:
        if fig is None:
            fig = plt.figure(figsize=figsize)
        ax = mplot3d.Axes3D(fig)
    return (fig, ax)

def set_info(ax="", title="", xlabel="", ylabel="", xticklabel=[""], yticklabel=[""]):
    if ax==None:
        fig, ax = plt.subplots()

    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticklabels([""] + xticklabel)
    ax.set_yticklabels([""] + yticklabel)
    return ax

def measure_canvas(nfigs, ncols=2, figsize=(6,4)):
    """
    @params nfigs   : (int) Total number of figures.
    @params ncols   : (int) The number of columns.
    @params figsize : (tuple) The figure size for 1 plot.
    """
    ncols, nrows = calc_rectangle_size(area=nfigs, w=ncols)
    w, h = figsize
    figsize=(w*ncols, h*nrows)
    return (ncols, nrows, figsize)