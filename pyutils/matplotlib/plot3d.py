# coding: utf-8
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits import mplot3d
from stl import mesh

from .layout import fig_ax_handler_3D

def stl2mpl_data(filename, ratio=1., seed=None):
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
    """Plot STL file.
    @params filename: (str) The file to load
    @params ratio   : (int)   The number of points to plot.
                      (float) The ratio of points to plot
    """
    poly_3D_collection, scale = stl2mpl_data(filename=filename, ratio=ratio, seed=seed)
    poly_3D_collection.set_alpha(alpha)
    poly_3D_collection.set_edgecolor(color)

    fig, ax = fig_ax_handler_3D(fig=None, ax=ax)
    ax.add_collection3d(poly_3D_collection)
    ax.auto_scale_xyz(scale, scale, scale)
    return ax