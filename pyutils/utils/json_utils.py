# coding: utf-8
import json
import datetime
import numpy as np

class PyUtilsJSONEncoder(json.JSONEncoder):
    """ Json encoder for Python data structures.

        Supports the following objects and types by default (``json.JSONEncoder``):
        
        +-------------------+---------------+
        | Python            | JSON          |
        +===================+===============+
        | dict              | object        |
        +-------------------+---------------+
        | list, tuple       | array         |
        +-------------------+---------------+
        | str               | string        |
        +-------------------+---------------+
        | int, float        | number        |
        +-------------------+---------------+
        | True              | true          |
        +-------------------+---------------+
        | False             | false         |
        +-------------------+---------------+
        | None              | null          |
        +-------------------+---------------+

    """
    def default(self, obj):
        """ Override this method to accommodate other types of data structures.

        Currently, supports the following objects and types by overriding.
        
        +-----------------------+---------------+
        | Python                | JSON          |
        +=======================+===============+
        | np.integar            | number(int)   |
        +-----------------------+---------------+
        | np.float              | number(float) |
        +-----------------------+---------------+
        | np.ndarray            | array         |
        +-----------------------+---------------+
        | np.random.RandomState | object        |
        +-----------------------+---------------+
        | datetime.datetime     | string        |
        +-----------------------+---------------+

        """
        # Numpy object
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.random.RandomState):
            dict_obj = dict(zip(
                ["MT19937", "unsigned_integer_keys", "pos", "has_gauss", "cached_gaussian"],
                obj.get_state()
            ))
            return dict_obj

        # datetime object
        elif isinstance(obj, datetime.datetime):
            return obj.isoformat()
        
        return super().default(obj)
    
def save_json(obj, file, ensure_ascii=False, indent=2, cls=PyUtilsJSONEncoder, **kwargs):
    """ Save the json file with easy-to-use arguments

    Args:
        obj (dict)             : Serialize ``obj`` as a JSON formatted stream.
        file (str)             : a text or byte string giving the path of the file to be opened.
        ensure_ascii (bool)    : If ``ensure_ascii`` is false, then the strings written to ``fp`` can contain non-ASCII characters if they appear in strings contained in ``obj``.
        indent (int)           : If ``indent`` is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. ``None`` is the most compact representation.
        cls (json.JSONEncoder) : To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the ``.default()`` method to serialize additional types), specify it with the ``cls`` kwarg; otherwise ``PyUtilsJSONEncoder`` is used.

    Example:
        >>> import datetime
        >>> from pyutils.utils import save_json
        >>> save_json(obj={"date": datetime.datetime.now(), "bool" : True}, file="sample.json")
        >>> with open("sample.json") as f:
        >>>     for line in f.readlines():
        >>>         print(line, end="")
        {
        "date": "2020-09-13T20:45:56.614838",
        "bool": true
        }

    """
    with open(file=file, mode="w", encoding="utf-8") as fp:
        json.dump(obj=obj, fp=fp, ensure_ascii=ensure_ascii, indent=indent, cls=cls, **kwargs)