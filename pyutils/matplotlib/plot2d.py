# coding: utf-8
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from ..utils import confusion_matrix

def plot_cumulative_ratio(data, labels=None, bins=10, width=0.8, reverse=False, ax=None, bar=False):
    num_data = len(data)
    _, bin_edges = np.histogram(a=data, bins=bins)
    X = bin_edges[:-1]
    if reverse: X = X[::-1]

    #=== Calcurate each group's plot information. ===
    if labels is None: labels = np.zeros_like(data)
    hists = np.zeros(shape=(1,bins))
    groups = np.unique(labels)
    for g in groups:
        hist, _ = np.histogram(a=data[labels==g], bins=bins)
        if reverse: hist = hist[::-1]
        # Memorize the "n" for each label.
        hists = np.r_[hists, np.cumsum(hist).reshape(1,-1)]

    # Plot
    fig, ax = fig_ax_handler_2D(ax=ax)
    hists /= num_data # Change number to ratio.
    bottoms = np.cumsum(hists, axis=0)
    cmap = plt.get_cmap("Accent", len(groups)).colors
    width = (bin_edges[1] - bin_edges[0])*width
    for i,(Y,g) in enumerate(zip(hists[1:], groups)):
        if bar:
            ax.bar(X, Y, bottom=bottoms[i], width=width, label=g, align="center", color=cmap[i])
        else:
            ax.plot(X, Y+bottoms[i], label=g, color=cmap[i], marker="o")
    return ax

def plot_model_cm(answer, predict, cmap=plt.cm.RdBu, answer_label="answer", predict_label="predict"):
    cm = confusion_matrix(answer, predict)
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.matshow(confmat, cmap=cmap, alpha=0.3)
    for i in range(confmat.shape[0]):
        for j in range(confmat.shape[1]):
            ax.text(x=j, y=i, s=confmat[i, j], va='center', ha='center')
    ax.set_title(predict_label)
    ax.set_ylabel(answer_label)
    return ax

def plot_TF_cm_2Dcond(result, fig=None, ax=None, vmin=0, vmax=1, cmap=plt.cm.RdBu, is_colorbar=False):
    """
    Plot the true/false value in 2 variable conditions.
    @param result: (ndarray) shape=(N, M, 2)
                   - N: The number of types of the condition 1.
                   - M: The number of types of the condition 2.
                   - 2: True / False vals.
    """
    N,M,_ = result.shape
    prob_cm = np.array([[result[i][j][0]/(sum(result[i][j])+1e-16) for j in range(M)] for i in range(N)])

    if (fig==None) or (ax==None):
        fig, ax = plt.subplots(figsize=(5, 5))
    cax = ax.matshow(prob_cm, cmap=cmap, alpha=0.3, vmin=vmin, vmax=vmax)
    if is_colorbar: fig.colorbar(cax)

    for i in range(N):
        for j in range(M):
            text = f"True:  {result[i][j][0]}\nFalse: {result[i][j][1]}\nProb:  {100*prob_cm[i][j]:.3f}%"
            ax.text(x=j, y=i, s=text, va='center', ha='center')
    return ax

def clear_grid(ax, x=True, y=True):
    if row:
        ax.tick_params(labelbottom=False, bottom=False)
        ax.set_xticklabels([])
    if col:
        ax.tick_params(labelleft=False, left=False)
        ax.set_yticklabels([])
    return ax