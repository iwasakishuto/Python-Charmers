# coding: utf-8
import numpy as np
from scipy.sparse import coo_matrix

from .generic_utils import handleKeyError

def take_centers(a):
    """Take a center values.

    Args:
        a (array) : Array
    
    Example:
        >>> from pyutils.utils import take_centers
        >>> take_centers([0,1,2,3,4,5])
        array([0.5, 1.5, 2.5, 3.5, 4.5])
        >>> take_centers([[0,1,2,3,4,5],[1,2,3,4,5,6]])
        array([[0.5, 1.5, 2.5, 3.5, 4.5],
            [1.5, 2.5, 3.5, 4.5, 5.5]])
    """
    a = np.asarray(a, dtype=np.float64)
    return (a[Ellipsis,1:] + a[Ellipsis,:-1])/2

def confusion_matrix(y_true, y_pred):
    """Compute confusion matrix to evaluate the accuracy of a classification.
    
    By definition a confusion matrix :math:`C` is such that :math:`C_{i, j}` is 
    equal to the number of observations known to be in group :math:`i` and predicted 
    to be in group :math:`j`.
    
    Thus in binary classification, the count of true negatives is
    :math:`C_{0,0}`, false negatives is :math:`C_{1,0}`, true positives is
    :math:`C_{1,1}` and false positives is :math:`C_{0,1}`.
    
    Args:
        y_true (array): Ground truth (correct) target values.
        y_pred (array): Estimated targets as returned by a classifier.
    
    Returns:
        cm (array): Confusion matrix whose i-th row and j-th column entry indicates 
                    the number of samples with true label being i-th class and prediced label being j-th class.

    References:
        `Wikipedia entry for the Confusion matrix <https://en.wikipedia.org/wiki/Confusion_matrix>`_ (Wikipedia and other references may use a different convention for axes)

    Examples:
        >>> from pyutils import confusion_matrix
        >>> y_true = [2, 0, 2, 2, 0, 1]
        >>> y_pred = [0, 0, 2, 2, 0, 2]
        >>> confusion_matrix(y_true, y_pred)
        array([[2, 0, 0],
            [0, 0, 1],
            [1, 0, 2]])
        >>> # In the binary case, we can extract true positives, etc as follows:
        >>> tn, fp, fn, tp = confusion_matrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
        >>> (tn, fp, fn, tp)
        (0, 2, 1, 1)
    """
    y_true = np.asarray(y_true).flatten(order='C')
    y_test = np.asarray(y_pred).flatten(order='C')
    num_labels = len(np.unique(np.concatenate([y_true, y_pred])))
    num_data   = len(y_true)
    cm = coo_matrix(
        (np.ones(num_data, dtype=np.int64), (y_true, y_pred)),
        shape=(num_labels, num_labels), dtype=np.int64,
    ).toarray()
    return cm