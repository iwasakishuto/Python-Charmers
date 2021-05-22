# coding: utf-8
import re
import argparse

from ..__meta__ import __project_name__
from .generic_utils import str_strip

def ListParamProcessorCreate(type=str):
    """Create a ListParamProcessor

    Args:
        type (type) : type of each element in list.

    Returns:
        ListParamProcessor (argparse.Action) : Processor which receives list arguments.

    Examples:
        >>> import argparse
        >>> from pycharmers.utils import ListParamProcessorCreate
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("--list_params", action=ListParamProcessorCreate())
        >>> args = parser.parse_args(args=["--list_params", "[あ, い, う]"])
        >>> args.list_params
        ['あ', 'い', 'う']
    """
    class ListParamProcessor(argparse.Action):
        """Receive List arguments.
        
        Examples:
            >>> import argparse
            >>> from pycharmers.utils import ListParamProcessor
            >>> parser = argparse.ArgumentParser()
            >>> parser.add_argument("--list_params", action=ListParamProcessor)
            >>> args = parser.parse_args(args=["--list_params", "[あ, い, う]"])
            >>> args.list_params
            ['あ', 'い', 'う']

        Note:
            If you run from the command line, execute as follows::
            
            $ python app.py --list_params "[あ, い, う]"

        """
        def __call__(self, parser, namespace, values, option_strings=None, **kwargs):
            match = re.match(pattern=r"(?:\[|\()(.+)(?:\]|\))", string=values)
            if match:
                values = [type(str_strip(e)) for e in match.group(1).split(",")]
            else:
                values = [type(values)]
            setattr(namespace, self.dest, values)
    return ListParamProcessor

class DictParamProcessor(argparse.Action):
    """Receive an argument as a dictionary.

    Raises:
        ValueError: You must give one argument for each one keyword.

    Examples:
        >>> import argparse
        >>> from pycharmers.utils import DictParamProcessor
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("--dict_params", action=DictParamProcessor)
        >>> args = parser.parse_args(args=["--dict_params", "foo = [a, b, c]", "--dict_params", "bar=d"])
        >>> args.dict_params
        {'foo': ['a', 'b', 'c'], 'bar': 'd'}
        >>> args = parser.parse_args(args=["--dict_params", "foo=a, bar=b"])
        ValueError: too many values to unpack (expected 2)

    Note:
        If you run from the command line, execute as follows::
        
        $ python app.py --dict_params "foo = [a, b, c]" --dict_params bar=c

    """
    def __call__(self, parser, namespace, values, option_strings=None):
        param_dict = getattr(namespace, self.dest) or {}  
        k, v = values.split("=")
        match = re.match(pattern=r"\[(.+)\]", string=str_strip(v))
        if match is not None:
            v = [str_strip(e) for e in match.group(1).split(",")]
        else:
            v = str_strip(v)
        param_dict[str_strip(k)] = v
        setattr(namespace, self.dest, param_dict)

class KwargsParamProcessor(argparse.Action):
    """Set a new argument.

    Examples:
        >>> import argparse
        >>> from pycharmers.utils import KwargsParamProcessor
        >>> parser = argparse.ArgumentParser()
        >>> parser.add_argument("--kwargs", action=KwargsParamProcessor)
        >>> args = parser.parse_args(args=["--kwargs", "foo=a", "--kwargs", "bar=b"])
        >>> (args.kwargs, args.foo, args.bar)
        (None, 'a', 'b')

    Note:
        If you run from the command line, execute as follows::
        
        $ python app.py --kwargs foo=a --kwargs bar=b

    """
    def __call__(self, parser, namespace, values, option_strings=None):
        k,v = values.split("=")
        setattr(namespace, k, v)

def cv2ArgumentParser(parser=None, prog="", description=None, add_help=True, **kwargs):
    """``ArgumentParser`` for OpenCV project.
    
    Args:
        --winname (str)       : Window name.
        --path (str)          : Path to video or image.
        --cam (int)           : The ID of the web camera.
        --ext (str)           : The extension for saved image.
        --gui-width (int)     : The width of the GUI tools.
        --gui-margin (int)    : The margin of GUI control tools.
        --gui-color (list)    : The background color of GUI tool.
        --monitor-size (list) : Monitor size. ( ``width`` , ``height`` )
        --autofit (bool)      : Whether to fit display size to window size.
        --twitter (bool)      : Whether you want to run for tweet. ( ``display_size`` will be () )
        --capture (bool)      : Whether you want to save as video.
    """
    if parser is None:
        parser = argparse.ArgumentParser(prog=prog, description=description, add_help=add_help, **kwargs)
    parser.add_argument("--winname",      type=str, default=prog+ f": {__project_name__}", help="Window name.")
    parser.add_argument("--path",         type=str, help="Path to video or image.")
    parser.add_argument("--cam",          type=int, default=0,   help="Define the id of the web camera. `cv2.VideoCapture( [ID] )`")
    parser.add_argument("--gui-width",    type=int, default=200, help="The width of the GUI tools.")
    parser.add_argument("--gui-margin",   type=int, default=10,  help="The margin of GUI control tools.")
    parser.add_argument("--gui-color",    action=ListParamProcessorCreate(type=int), default=(49, 52, 49), help="The background color of GUI tool.")
    parser.add_argument("--ext",          type=str, default=".jpg", help="The extension for saved image.")
    parser.add_argument("--monitor-size", action=ListParamProcessorCreate(type=int), default=(1440, 960), help="Monitor size. (width, height)")
    parser.add_argument("--autofit",      action="store_true", help="Whether to fit display size to window size.")
    parser.add_argument("--twitter",      action="store_true", help="Whether you want to run for tweet. ( ``display_size`` will be ( ``1300`` , ``730`` ) ).")
    parser.add_argument("--capture",      action="store_true", help="Whether you want to save as video.")
    return parser

def define_neg_sides(args:argparse.Namespace, prefix:str="un_"):
    """Define the negative side in ``argparse.Namespace`` 

    I know that ``action="store_false"`` can do the similar, but I defined this function because of the readability and ease of use of the code.

    Args:
        args (argparse.Namespace) : Simple object for storing attributes.
        prefix (str, optional)    : Prefix indicating ``"Negative"`` . Defaults to ``"un_"`` .

    Examples:
        >>> import argparse
        >>> from pycharmers.utils import define_neg_sides
        >>> parser = argparse.ArgumentParser(prog="Python-Charmers Examples")
        >>> parser.add_argument("un_debug", action="store_true")
        >>> parser.add_argument("-ur", "--un-reload", action="store_true")
        >>> args = parser.parse_args([])
        >>> define_neg_sides(args)
        >>> print(f"debug={args.debug}, reload={args.reload}, un_debug={args.un_debug}, un_reload={args.un_reload}")
            debug=False, reload=True, un_debug=True, un_reload=False
        >>> args = parser.parse_args(["-ur"])
        >>> define_neg_sides(args)
        >>> print(f"debug={args.debug}, reload={args.reload}, un_debug={args.un_debug}, un_reload={args.un_reload}")
            debug=False, reload=False, un_debug=True, un_reload=True
    """
    for k,v in args._get_kwargs():
        if k.startswith(prefix) and isinstance(v,bool):
            new_k = k[len(prefix):]
            if (not hasattr(args, new_k)):
                setattr(args, new_k, not v)