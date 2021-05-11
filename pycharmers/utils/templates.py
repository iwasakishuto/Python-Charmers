#coding: utf-8
import os
from ._path import TEMPLATES_DIR
from ._colorings import toBLUE
from jinja2 import Environment, FileSystemLoader, TemplateNotFound, Template

def render_template(template_name_or_string, context={}, path=None, searchpath=TEMPLATES_DIR, **envkwargs):
    """Render Template.

    Args:
        template_name_or_string (str) : The name of the template to be rendered or a string.
        context (dict)                : The variables that should be available in the context of the template.
        path (str)                    : If given, output to ``path`` file.
        searchpath (str)              : (Default= ``TEMPLATES_DIR`` )

    Examples:
        >>> import matplotlib
        >>> from pycharmers.utils import render_template
        >>> render_template(
        ...     template_name_or_string="fonts.html", 
        ...     context={"fonts": sorted(set([f.name for f in matplotlib.font_manager.fontManager.ttflist]))}
        >>> )
    """
    env = Environment(loader=FileSystemLoader(searchpath=searchpath), **envkwargs)
    try:
        template = env.get_template(name=template_name_or_string)
    except TemplateNotFound:
        template = env.from_string(source=template_name_or_string)
    string = template.render(**context)
    if path is None:
        print(string)
    else:
        with open(path, mode="w") as f:
            f.write(string)
        print(f"Content was saved at {toBLUE(path)}.")

def _mk_func(fn, name):
    """Make a function which is for documentation.

    Args:
        fn (str): Filename.

    Returns:
        function: function which has the google docstrings (HTML content is contained.)

    Examples:
        >>> from pycharmers.utils.templates import _mk_func
        >>> func = _mk_func(fn="base.html", name="base_html")
    """
    fp = os.path.join(TEMPLATES_DIR, fn)
    with open(fp, mode="r") as f:
        code = "\t".join(f.readlines())
    def func():
        return fp
    func.__doc__ = f"""Return the path to ``TEMPLATES_DIR``/{fn}
    
    Returns:
        str : Where this file is.
    
    The contents of the file are as follows:

    .. code-block:: html
        
        {code}

    Examples:
        >>> from pycharmers.utils.templates import {name}
        >>> {name}()
    """
    return func

for fn in os.listdir(TEMPLATES_DIR):
    if fn[-5:] != ".html": continue
    name = fn.replace(".", "_")
    exec(f"{name} = _mk_func('{fn}', '{name}')")

class defFunction():
    def __init__(self, func_name, short_description="", description="", is_method=False):
        self.func_name = func_name
        self.short_description = short_description
        self.description = description
        self.is_method = is_method
        self.argwidth = 0
        self.arguments = {}

    def set_example(self, prefix="", suffix=""):
        if prefix=="":
            prefix = ">>> " + self.func_name + "("
        self.example_prefix = prefix
        self.example_suffix = suffix
        self.examples=True

    def set_returns(self, name, type, description=""):
        self.returns = f"{name} ({type.__name__}): {description}"
        
    def sort_arguments(self):
        self.arguments = dict(sorted(self.arguments.items(), key=lambda x: x[1]["is_required"], reverse=True))
        
    def set_argument(self, name, default, example=None, description="", type=str, is_required=True, **kwargs):
        name_type = f"{name} ({type.__name__})"
        argumeta = {
            "type": type,
            "is_required": is_required,
            "default": default,
            "example": example,
            "description": description,
            "name_type": name_type,
        }
        argumeta.update(kwargs)
        self.arguments[name] = argumeta
        self.argwidth = max(self.argwidth, len(name_type))
        
    def set_arguments(self, **arguments):
        for argname, argmeta in arguments.items:
            self.set_argument(name=argname, **argmeta)

    def create(self):
        self.sort_arguments()
        render_template(
            template_name_or_string="def.html",
            context=self.__dict__,
            searchpath=TEMPLATES_DIR,
        )