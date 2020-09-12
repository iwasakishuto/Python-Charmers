# coding: utf-8
import numpy as np

def take_a_between(a):
    a = np.asarray(a, dtype=float)
    return a[1:] + a[:-1]