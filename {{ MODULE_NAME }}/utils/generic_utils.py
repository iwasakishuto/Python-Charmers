# coding: utf-8
import re
import argparse
import datetime

from .coloring_utils import toRED, toBLUE, toGREEN

def handleKeyError(lst, **kwargs):
    k,v = kwargs.popitem()
    if v not in lst:
        lst = ', '.join([f"'{e}'" for e in lst])
        raise KeyError(f"Please choose the argment {toBLUE(k)} from {lst}. you chose {toRED(v)}")

def handleTypeError(types, **kwargs):
    type2str = lambda t: re.sub(r"<class '(.*?)'>", r"\033[34m\1\033[0m", str(t))
    k,v = kwargs.popitem()
    if not any([isinstance(v,t) for t in types]):
        str_true_types  = ', '.join([type2str(t) for t in types])
        srt_false_type = type2str(type(v))
        if len(types)==1:
            err_msg = f"must be {str_true_types}"
        else:
            err_msg = f"must be one of {str_true_types}"
        raise TypeError(f"{toBLUE(k)} {err_msg}, not {toRED(srt_false_type)}")

def mk_class_get(all_classes={}, gummy_abst_class=[], genre=""):
    if not isinstance(gummy_abst_class, list):
        gummy_abst_class = [gummy_abst_class]
    def get(identifier, **kwargs):
        if isinstance(identifier, str):
            identifier = identifier.lower()
            handleKeyError(lst=list(all_classes.keys()), identifier=identifier)
            instance = all_classes.get(identifier)(**kwargs)
        else:
            handleTypeError(types=[str] + gummy_abst_class, identifier=identifier)
            instance = identifier
        return instance
    get.__doc__ = f"""
    Retrieves a {{ PACKAGE_NAME }} {genre.capitalize()} instance.
    @params identifier : {genre.capitalize()} identifier, string name of a {genre}, or
                         a {{ PACKAGE_NAME }} {genre.capitalize()} instance.
    @params kwargs     : parametes for class initialization.
    @return {genre:<11}: A {{ PACKAGE_NAME }} {genre.capitalize()} instance.
    """
    return get

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

def str_strip(string):
    return re.sub(pattern=r"[\s 　]+", repl=" ", string=string).strip()

def now_str():
    return datetime.datetime.now().strftime("%Y-%m-%d@%H.%M.%S")