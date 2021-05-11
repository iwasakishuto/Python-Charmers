# coding: utf-8
def test_plot_stl_file():
    from pycharmers.matplotlib import plot_stl_file, FigAxes_create, set_ax_info
    fig, ax = FigAxes_create(figsize=(8,8), projection="3d", nplots=1)[0]
    plot_stl_file("Scorpion.stl", ax=ax, ratio=.5, alpha=0.01, color="red")
    set_ax_info(ax, title="Scorpion")
    fig.savefig("Scorpion.png")


