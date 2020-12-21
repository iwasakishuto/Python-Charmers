#coding: utf-8
import os
from ._path import TEMPLATES_DIR
from ._colorings import toBLUE
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

def render_template(source, content={}, path=None, searchpath=TEMPLATES_DIR, **envkwargs):
    env = Environment(loader=FileSystemLoader(searchpath=searchpath), **envkwargs)
    try:
        template = env.get_template(name=source)
    except TemplateNotFound:
        template = env.from_string(source=source)
    string = template.render(**content)
    if path is None:
        print(string)
    else:
        with open(path, mode="w") as f:
            f.write(string)
        print(f"Content was saved at {toBLUE(path)}.")

def _mk_func(fn):  
    fp = os.path.join(TEMPLATES_DIR, fn)
    with open(fp, mode="r") as f:
        code = "\t".join(f.readlines())
    def func():
        return fp
    func.__doc__ = f"""Return ``TEMPLATES_DIR``/{fn}
    
    Returns:
        str : Where this file is.
    The contents of the file are as follows:
    .. code-block:: html
        
        {code}
    """
    return func

for fn in os.listdir(TEMPLATES_DIR):
    if fn[-5:] != ".html": continue
    name = fn.replace(".", "_")
    exec(f"{name} = _mk_func('{fn}')")