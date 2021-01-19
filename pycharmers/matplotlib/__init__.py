# coding: utf-8
from . import cmaps
from . import layout
from . import plot2d
from . import plot3d


from .cmaps import (BASE_COLORS, CSS4_COLORS, XKCD_COLORS, TABLEAU_COLORS, FAMOUS_COLOR_PALETTES)
from .cmaps import plot_color_palettes
from .cmaps import plot_cmap_samples
from .cmaps import plot_cmap_category_samples
from .cmaps import color_dict_create

from .layout import FigAxes_create
from .layout import set_ax_info
from .layout import measure_canvas
from .layout import clear_grid
from .layout import show_all_fonts
from .layout import mpljapanize

from .plot2d import plot_hist
from .plot2d import plot_cumulative_ratio
from .plot2d import plot_classification_performance
from .plot2d import plot_lines
from .plot2d import plot_radar_charts

from .plot3d import stl2mpl_data
from .plot3d import plot_stl_file