# coding: utf-8
from . import cmaps
from . import layout
from . import plot2d
from . import plot3d


from .cmaps import (COLOR_BLACK, COLOR_BLUE, COLOR_CYAN, COLOR_GREEN, COLOR_MAGENTA, COLOR_RED, COLOR_WHITE, COLOR_YELLOW, 
                    BASE_COLORS, CSS4_COLORS, XKCD_COLORS, TABLEAU_COLORS, FAMOUS_COLOR_PALETTES)
from .cmaps import plot_color_palettes
from .cmaps import plot_cmap_samples
from .cmaps import plot_cmap_category_samples
from .cmaps import color_dict_create

from .layout import FigAxes_create
from .layout import set_ax_info
from .layout import measure_canvas
from .layout import clear_grid

from .plot2d import plot_hist
from .plot2d import plot_cumulative_ratio
from .plot2d import plot_classification_performance
from .plot2d import plot_lines

from .plot3d import stl2mpl_data
from .plot3d import plot_stl_file