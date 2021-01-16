# coding: utf-8
def test_plot_classification_performance():
    import numpy as np
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import plot_classification_performance
    rnd = np.random.RandomState(123)
    y_true = rnd.randint(low=0, high=4, size=100)
    y_pred = rnd.randint(low=0, high=4, size=100)
    plot_classification_performance(y_true=y_true, y_pred=y_pred)
    plt.show()

def test_plot_lines():
    import matplotlib.pyplot as plt
    from pycharmers.matplotlib import set_ax_info, plot_lines
    #=== Data ===
    names = ["A", "B", "C", "D", "E", "F", "G"]
    dates = ["early-Jan.","mid-Jan.","late-Jan.","early-Feb.","mid-Feb.","late-Feb.","early-Mar.","mid-Mar.","late-Mar."]
    month_colors = ["#e30013", "#4b73b6", "#f09eb0"]
    schedule_hope = [None, None, 4, 6, 2, 0, 3]
    schedule_inconvenient = [[], [2], [1, 2, 3], [0, 1, 2, 5, 7, 8], [1, 3, 4, 5], [1, 2, 5], [0, 5, 6]]
    num_names = len(names)
    num_dates = len(dates)
    #=== Plot ===
    fig, ax = plt.subplots(figsize=(12,8), dpi=80, facecolor="white")
    ax = plot_lines(data=schedule_inconvenient, ax=ax, transpose=True, color="black", label="Inconvenient")
    ax.scatter(x=schedule_hope, y=[i for i in range(len(schedule_hope))], color="red", s=100, marker="*", label="Hope")
    for i,color in enumerate(month_colors):
        ax.fill((i*3-0.5,i*3-0.5,(i+1)*3-0.5,(i+1)*3-0.5), (num_names,0,0,num_names), color=color, alpha=0.1, label=dates[i*3].split("-")[-1]) 
    #=== Decoration ===
    ax = set_ax_info(ax, **{
        "xticks":      {"ticks" : [i for i in range(num_dates)]},
        "xticklabels": {"labels": dates, "fontsize":16},
        "yticks":      {"ticks" : [i for i in range(num_names)]},
        "yticklabels": {"labels": names, "fontsize":16},
        "title":       {"label": "Results of Schedule Adjustment", "fontsize":20},
    })
    ax.legend()
    plt.tight_layout()
    plt.show()

