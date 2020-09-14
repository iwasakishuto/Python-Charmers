# coding: utf-8
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from ..utils.generic_utils import handleKeyError, flatten_dual
from .layout import FigAxes_create, set_ax_info

Category2Cmaps = {
    "Perceptually Uniform Sequential" : ["inferno", "magma", "plasma", "viridis"],
    "Sequential"                      : ["Blues", "BuGn", "BuPu", "GnBu", "Greens", "Greys", "OrRd", "Oranges", "PuBu", "PuBuGn", "PuRd", "Purples", "RdPu", "Reds", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd"],
    "Sequential (2)"                  : ["binary", "gist_yarg", "gist_gray", "gray", "bone", "pink", "spring", "summer", "autumn", "winter", "cool", "Wistia", "hot", "afmhot", "gist_heat", "copper"],
    "Diverging"                       : ["PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu", "RdYlBu", "RdYlGn", "Spectral", "coolwarm", "bwr", "seismic"],
    "Qualitative"                     : ["Pastel1", "Pastel2", "Paired", "Accent", "Dark2", "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b", "tab20c"],
    "Miscellaneous"                   : ["flag", "prism", "ocean", "gist_earth", "terrain", "gist_stern", "gnuplot", "gnuplot2", "CMRmap", "cubehelix", "brg", "hsv", "gist_rainbow", "rainbow", "jet", "nipy_spectral", "gist_ncar"],
}
Supported_Cmap_Categories = list(Category2Cmaps.keys())
Supported_Cmaps = flatten_dual(Category2Cmaps.values())

def plot_cmap_samples(cmap_name="all", ax=None, dpi=10):
    """Plot color map samples

    Args:
        cmap_name (str) : The name of a color map known to ``matplotlib``
        ax (Axes)       : The ``Axes`` instance.
        dpi (int)       : The resolution of the figure. (The size of matrix.)

    Example:
        >>> from pyutils.matplotlib import plot_cmap_samples
        >>> # plot specified color map
        >>> ax = plot_cmap_samples(cmap_name="jet")
        >>> # plot All color maps
        >>> plot_cmap_samples(cmap_name="all")
        >>> # plot color map with different dpi (Dots per inch)
        >>> ax = plot_cmap_samples(cmap_name="Pastel1", dpi=9)
    """
    if cmap_name.lower() == "all":
        fig, axes = FigAxes_create(nfigs=len(Supported_Cmaps), ncols=4, figsize=(4,4))
        for ax,cmap_name in zip(axes, Supported_Cmaps):            
            ax = plot_cmap_samples(cmap_name=cmap_name, ax=ax)
        plt.show()
    else:
        handleKeyError(lst=Supported_Cmaps + ["all"], cmap_name=cmap_name)
        fig, ax = FigAxes_create(fig=None, ax=ax)
        matrix = np.arange(np.power(dpi,2)).reshape(dpi,dpi)
        ax.matshow(matrix, cmap=cmap_name)
        ax = set_ax_info(ax, title=cmap_name, xticks=[], yticks=[])
        return ax

def plot_cmap_category_samples(category="all"):
    """Plot all colormap samples in a category

    Args:
        category (str) : the name of a color map category.

    Example:
        >>> from pyutils.matplotlib import plot_cmap_samples
        >>> # plot specified color map category
        >>> plot_cmap_category_samples(category="Sequential")
        >>> # plot All color map categories
        >>> plot_cmap_category_samples(category="all")
    """

    if category.lower()=="all":
        for k in Supported_Cmap_Categories:
            plot_cmap_category_samples(category=k)
    else:
        handleKeyError(lst=Supported_Cmap_Categories + ["all"], category=category)
        cmap_list = Category2Cmaps.get(category)

        num_cmaps = len(cmap_list)
        fig, axes = plt.subplots(num_cmaps, 2, figsize=(9, num_cmaps*0.35))
        fig.subplots_adjust(wspace=0.4)
        axes[0][0].set_title(f"{category} colormaps", fontsize=14, x=1.2)

        data = np.linspace(0, 1, 256).reshape(1, -1)
        def plot_color_map(ax, name):
            ax.imshow(data, aspect="auto", cmap=name)
            ax.set_axis_off()
            ax.text(-10, 0, name, va="center", ha="right", fontsize=10)
            return ax

        for [axL, axR], name in zip(axes, cmap_list):
            axL = plot_color_map(ax=axL, name=name)
            axR = plot_color_map(ax=axR, name=f"{name}_r")
        plt.show()