# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from stl import mesh

from .layout import FigAxes_create, set_ax_info

def stl2mpl_data(filename, ratio=1., seed=None):
    """Create A collection of 3D polygons from STL file.

    Note:
        When converting STL data to 3D Polygons, the number of data points becomes extremely large, so it is better to do sampling using the ``ratio`` parameter.

    Args:
        filename (str)    : The STL file to load
        ratio (float/int) : Sampling percentage or the exact number of sampling data points.
        seed (int)        : Value to ensure sampling reproducibility

    References:        
        `numpy-stl - PyPI <https://pypi.org/project/numpy-stl/>`_
    """
    # Load the STL files and add the vectors to the plot
    stl_data = mesh.Mesh.from_file(filename)
    stl_vector = stl_data.vectors
    stl_points = stl_data.points
    num_stl_data_points = len(stl_vector)
    print(f"The number of STL data points: {num_stl_data_points:,}")

    # Extract only some of them.
    if isinstance(ratio, float):
        num_plot_data_points = int(num_stl_data_points*ratio)
    else:
        num_plot_data_points = int(ratio)
    num_plot_data_points = max(0, min(num_plot_data_points, num_stl_data_points))
    print(f"The number of data points to plot: {num_plot_data_points:,}")
    random_data_point = np.random.choice(a=np.arange(0, num_stl_data_points), size=num_plot_data_points, replace=False)
    stl_vector = stl_vector[random_data_point]
    stl_points = stl_points[random_data_point]

    poly_3D_collection = mplot3d.art3d.Poly3DCollection(stl_vector)
    scale = stl_points.flatten(order='C')
    return (poly_3D_collection, scale)

def plot_stl_file(filename, ax=None, ratio=1., seed=None, alpha=1, color=None):
    """Plot STL data.

    Note:
        When converting STL data to 3D Polygons, the number of data points becomes extremely large, so it is better to do sampling using the ``ratio`` parameter.

    Args:
        filename (str)    : The STL file to load
        ax (Axes)         : The 3D ``Axes`` instance.
        ratio (float/int) : Sampling percentage or the exact number of sampling data points.
        seed (int)        : Value to ensure sampling reproducibility
        alpha (float)     : The alpha blending value, between 0 (transparent) and 1 (opaque).
        color (str)       : The edge color of the marker.

    Examples:
        >>> from pycharmers.matplotlib import plot_stl_file, FigAxes_create, set_ax_info
        >>> fig, ax = FigAxes_create(figsize=(8,8), projection="3d", nplots=1)[0]
        >>> plot_stl_file("Scorpion.stl", ax=ax, ratio=.5, alpha=0.01, color="red")
        >>> set_ax_info(ax, title="Scorpion")
        >>> fig.savefig("Scorpion.png")

    References:        
        If you want to see the result of the ``Examples``, see `my tweet <https://twitter.com/cabernet_rock/status/1304751796233986048>`_

    +-----------------------------------------------------------+
    |                         Results                           |
    +===========================================================+
    | .. image:: _images/matplotlib.plot3d.plot_stl_file.jpg    |
    +-----------------------------------------------------------+
    """
    poly_3D_collection, scale = stl2mpl_data(filename=filename, ratio=ratio, seed=seed)
    poly_3D_collection.set_alpha(alpha)
    poly_3D_collection.set_edgecolor(color)
    fig, ax = FigAxes_create(fig=None, ax=ax, projection="3d")
    ax.add_collection3d(poly_3D_collection)
    ax.auto_scale_xyz(scale, scale, scale)
    return ax