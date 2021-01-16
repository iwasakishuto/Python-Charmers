# coding: utf-8
def test_confusion_matrix():
    from pycharmers import confusion_matrix
    y_true = [2, 0, 2, 2, 0, 1]
    y_pred = [0, 0, 2, 2, 0, 2]
    confusion_matrix(y_true, y_pred)
    # array([[2, 0, 0],
    #     [0, 0, 1],
    #     [1, 0, 2]])
    # In the binary case, we can extract true positives, etc as follows:
    tn, fp, fn, tp = confusion_matrix([0, 1, 0, 1], [1, 1, 1, 0]).ravel()
    (tn, fp, fn, tp)
    # (0, 2, 1, 1)

