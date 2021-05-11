# coding: utf-8
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib._color_data as mcd
from matplotlib import cm

from ..utils.generic_utils import handleKeyError, flatten_dual
from .layout import FigAxes_create, set_ax_info, clear_grid

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

#====== COLOR VARNAMES (RGB) ======
BASE_COLORS = mcd.BASE_COLORS
CSS4_COLORS = mcd.CSS4_COLORS
XKCD_COLORS = {name[5:]:color for name,color in mcd.XKCD_COLORS.items()}
TABLEAU_COLORS = {name[4:]:color for name,color in mcd.TABLEAU_COLORS.items()}
FAMOUS_COLOR_PALETTES = {
    "base"    : BASE_COLORS,
    "css4"    : CSS4_COLORS,
    "xkcd"    : XKCD_COLORS,
    "tableau" : TABLEAU_COLORS,
}
#==============================

def plot_color_palettes(palette_name="all"):
    """Plot color palettes

    Args:
        palette_name (str) : The name of a color map known to ``matplotlib``

    Example:
        >>> from pycharmers.matplotlib import plot_color_palettes
        >>> # plot specified color map
        >>> plot_color_palettes(palette_name="xkcd")
        >>> # plot All color maps
        >>> plot_color_palettes(palette_name="all")
    """
    if palette_name.lower() == "all":
        for palette_name in FAMOUS_COLOR_PALETTES.keys():            
            plot_color_palettes(palette_name=palette_name)
    else:
        handleKeyError(lst=list(FAMOUS_COLOR_PALETTES.keys()) + ["all"], palette_name=palette_name)
        palettes = FAMOUS_COLOR_PALETTES.get(palette_name)
        palettes = sorted(palettes.items(), key=lambda x:x[1])
        fig, axes = FigAxes_create(figsize=(4, 0.2), nfigs=len(palettes), ncols=4, axis=1)
        axes[0].set_title(f"Palette: {palette_name}", fontsize=18, x=2)
        for ax,(name,color) in zip(axes, palettes):
            ax.hlines(y=0, xmin=0, xmax=0.5, color=color, linewidth=10) 
            ax.text(x=0.55, y=0, s=name, fontsize=12, horizontalalignment="left", verticalalignment="center")
            ax = clear_grid(ax, pos=["x","y","all"])
            ax.set_xlim(0, 1)
        plt.show()

def plot_cmap_samples(cmap_name="all", ax=None, dpi=10):
    """Plot color map samples

    Args:
        cmap_name (str) : The name of a color map known to ``matplotlib``
        ax (Axes)       : The ``Axes`` instance.
        dpi (int)       : The resolution of the figure. (The size of matrix.)

    Example:
        >>> from pycharmers.matplotlib import plot_cmap_samples
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
        >>> from pycharmers.matplotlib import plot_cmap_samples
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

def color_dict_create(keys, cmap="jet", reverse=False, max_val=1):
    """Create a color dict.

    Args:
        keys (int / list)              : (The number of) Keys of the color dict
        cmap (str / matplotlib.colors) : Color map.
        reverse (bool)                 : Whether to reverse the color.
        max_val (int)                  : Max value of color code.

    Returns:
        color_dict : key -> color.

    Examples:
        >>> import matplotlib.pyplot as plt
        >>> from pycharmers.matplotlib import color_dict_create
        >>> color_dict_create(keys=["a","b","c"], cmap="jet")
        {
            'b': (0.0, 0.0, 0.5, 1.0),
            'c': (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
            'a': (0.5, 0.0, 0.0, 1.0)
        }
        >>> color_dict_create(keys=3, cmap="jet")
        {
            0: (0.0, 0.0, 0.5, 1.0),
            1: (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
            2: (0.5, 0.0, 0.0, 1.0)
        }
        >>> color_dict_create(keys=["a","b","c"], cmap=plt.get_cmap("jet"))
        {
            'b': (0.0, 0.0, 0.5, 1.0),
            'c': (0.4901960784313725, 1.0, 0.4775458570524984, 1.0),
            'a': (0.5, 0.0, 0.0, 1.0)
        }
    """
    if not isinstance(cmap, colors.Colormap):
        handleKeyError(lst=Supported_Cmaps, cmap=cmap)
        if reverse: cmap += "_r"
        cmap = plt.get_cmap(cmap)

    if isinstance(keys, int):
        N = keys-1
        iterator = range(keys)
    else:
        unique_keys = set(keys)
        N = len(unique_keys)-1
        iterator = unique_keys
    color_dict = {
        key: tuple([
            max_val*e if i<3 else e for i,e in enumerate(cmap(n/N))
        ]) for n,key in enumerate(iterator)
    }
    return color_dict
