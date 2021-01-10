# coding: utf-8
import pandas as pd
from .generic_utils import list2name

def flatten_multi_columns(df, how="snake"):
    """
    Args:
        df (DataFrame) : Two-dimensional, size-mutable, potentially heterogeneous tabular data.
        how (str)      : How to convert dual column labels to one-column name.
    """
    df = df.copy(deep=True)
    df.columns = [list2name(col) if col[0]!=col[1] else col[0] for col in df.columns.values]
    return df