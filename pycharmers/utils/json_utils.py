# coding: utf-8
import json
import datetime
import numpy as np
from .generic_utils import str_strip

class PythonCharmersJSONEncoder(json.JSONEncoder):
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
    
def dumps_json(obj, ensure_ascii=False, indent=2, cls=PythonCharmersJSONEncoder, flatten_list=True, **kwargs):
    """dumps Json object to String.

    Args:
        obj (dict)             : Serialize ``obj`` as a JSON formatted stream.
        ensure_ascii (bool)    : If ``ensure_ascii`` is false, then the strings written to ``fp`` can contain non-ASCII characters if they appear in strings contained in ``obj``.
        indent (int)           : If ``indent`` is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. ``None`` is the most compact representation.
        cls (json.JSONEncoder) : To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the ``.default()`` method to serialize additional types), specify it with the ``cls`` kwarg; otherwise ``PythonCharmersJSONEncoder`` is used.
        flatten_list (bool)    : Whether you want to flatten the list or not.

    Example:
        >>> import datetime
        >>> from pycharmers.utils import dumps_json
        >>> print(dumps_json(obj={
        ...    "date": datetime.datetime.now(), 
        ...     "bool" : True,
        ...     "dual_list": [[1,2,3],[4,5,6]]
        >>> }))
        {
            "date": "2020-12-07T23:28:49.311962",
            "bool": true,
            "dual_list": [
                [1, 2, 3],
                [4, 5, 6]
            ]
        }
    """
    if flatten_list:
        encoder = cls(ensure_ascii=ensure_ascii, indent=indent)
        chunks=[]; num_brackets=0
        for e in encoder.iterencode(obj, _one_shot=True):
            if e[0]=="[": num_brackets+=1
            elif e[0]=="]": num_brackets-=1    
            if num_brackets>1: e = str_strip(e)
            chunks.append(e)
        text = ''.join(chunks).replace("[ ", "[")
    else:
        text = json.dumps(obj=obj, ensure_ascii=ensure_ascii, indent=indent, cls=cls, **kwargs)
    text = text.replace("NaN", "null")
    return text

def save_json(obj, file, ensure_ascii=False, indent=2, cls=PythonCharmersJSONEncoder, flatten_list=True, **kwargs):
    """ Save the json file with easy-to-use arguments

    Args:
        obj (dict)             : Serialize ``obj`` as a JSON formatted stream.
        file (str)             : a text or byte string giving the path of the file to be opened.
        ensure_ascii (bool)    : If ``ensure_ascii`` is false, then the strings written to ``fp`` can contain non-ASCII characters if they appear in strings contained in ``obj``.
        indent (int)           : If ``indent`` is a non-negative integer, then JSON array elements and object members will be pretty-printed with that indent level. An indent level of 0 will only insert newlines. ``None`` is the most compact representation.
        cls (json.JSONEncoder) : To use a custom ``JSONEncoder`` subclass (e.g. one that overrides the ``.default()`` method to serialize additional types), specify it with the ``cls`` kwarg; otherwise ``PythonCharmersJSONEncoder`` is used.
        flatten_list (bool)    : Whether you want to flatten the list or not.

    Example:
        >>> import datetime
        >>> from pycharmers.utils import save_json
        >>> save_json(obj={"date": datetime.datetime.now(), "bool" : True}, file="sample.json")
        >>> with open("sample.json") as f:
        >>>     for line in f.readlines():
        >>>         print(line, end="")
        {
            "date": "2020-09-13T20:45:56.614838",
            "bool": true
        }

    """
    text = dumps_json(
        obj=obj, 
        ensure_ascii=ensure_ascii, 
        indent=indent, 
        cls=cls, 
        flatten_list=flatten_list,
        **kwargs
    )    
    with open(file=file, mode="w", encoding="utf-8") as fp:
        fp.write(text)