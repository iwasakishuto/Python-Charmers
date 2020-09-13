# coding: utf-8
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib import cm

from ..utils.generic_utils import handleKeyError, flatten_dual

Category2Cmaps = {
    "Perceptually Uniform Sequential" : ["inferno", "magma", "plasma", "viridis"],
    "Sequential"                      : ["Blues", "BuGn", "BuPu", "GnBu", "Greens", "Greys", "OrRd", "Oranges", "PuBu", "PuBuGn", "PuRd", "Purples", "RdPu", "Reds", "YlGn", "YlGnBu", "YlOrBr", "YlOrRd"],
    "Sequential (2)"                  : ["binary", "gist_yarg", "gist_gray", "gray", "bone", "pink", "spring", "summer", "autumn", "winter", "cool", "Wistia", "hot", "afmhot", "gist_heat", "copper"],
    "Diverging"                       : ["PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu", "RdYlBu", "RdYlGn", "Spectral", "coolwarm", "bwr", "seismic"],
    "Qualitative"                     : ["Pastel1", "Pastel2", "Paired", "Accent", "Dark2", "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b", "tab20c"],
    "Miscellaneous"                   : ["flag", "prism", "ocean", "gist_earth", "terrain", "gist_stern", "gnuplot", "gnuplot2", "CMRmap", "cubehelix", "brg", "hsv", "gist_rainbow", "rainbow", "jet", "nipy_spectral", "gist_ncar"],
}
Supported_Cmaps = flatten_dual(Category2Cmaps.values())

def get_cmap():
    print()

def plot_cmap_samples(cmap_name="all"):
    if cmap_name.lower() == "all":
        for e in Supported_Cmaps:
            plot_cmap_samples(cmap_name=e)

def plot_cmap_category_samples(category_name="all"):
    if category.lower()=="all":
        for k in Category2Cmaps.keys():
            plot_cmap_samples(category=k)
    else:
        handleKeyError(lst=list(Category2Cmaps.keys()) + ["all"], category=category)
        cmap_list = Category2Cmaps.get(category)

        num_cmaps = len(cmap_list)
        fig, axes = plt.subplots(num_cmaps, 2, figsize=(9, num_cmaps * 0.35))
        fig.subplots_adjust(wspace=0.4)
        axes[0][0].set_title(category + ' colormaps', fontsize=14, x=1.2)

        data = np.linspace(0, 1, 256).reshape(1, -1)
        def plot_color_map(ax, name):
            ax.imshow(data, aspect='auto', cmap=name)
            ax.set_axis_off()
            ax.text(-10, 0, name, va='center', ha='right', fontsize=10)
            return ax

        for [axL, axR], name in zip(axes, cmap_list):
            axL = plot_color_map(ax=axL, name=name)
            axR = plot_color_map(ax=axR, name=name + '_r')
        plt.show()