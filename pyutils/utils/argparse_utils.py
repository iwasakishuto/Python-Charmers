# coding: utf-8

import argparse

class MonoParamProcessor(argparse.Action):
    """
    Receive an argument as a dictionary.
    =====================================================
    (sample)
    $ python argparse_handler.py --dict_param foo=a --dict_param bar=b
    >>> {'foo': 'a', 'bar': 'b'}
    """
    def __call__(self, parser, namespace, values, option_strings=None):
        param_dict = getattr(namespace,self.dest,[])
        if param_dict is None:
            param_dict = {}

        k, v = values.split("=")
        param_dict[k] = v
        setattr(namespace, self.dest, param_dict)