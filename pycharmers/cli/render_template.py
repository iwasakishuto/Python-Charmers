#coding: utf-8
import os
import re
import sys
import json
import shutil
import argparse
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from ._clipath import PYCHARMERS_CLI_RENDER_TEMPLATES_DIR
from ..utils._colorings import toBLUE, toGREEN

def add_title_prefix_for_rawmeta(fp, ext=".raw"):
    fp = str(fp)
    with open(fp, mode="r") as fr:
        content = fr.readlines()
        title = content[0]
    for key,fa in {
        "(R)"      : "fab fa-r-project",
        "(python)" : "fab fa-python",
    }.items():
        if key in title:
            title = f': <i class="{fa}" style="color: #3e978b"></i>&thinsp;'.join(title.split(": "))
    content[0] = title
    with open(fp.replace(ext, ""), mode="w") as fw:
        fw.writelines(content)

def add_extra_keys(keys, data):
    if "photowall" in data:
        photowall = data["photowall"]
        if photowall.get("administration", False):
            keys.append("administration")
        if photowall.get("extraction", False):
            keys.append("extraction")

def render_template(argv=sys.argv[1:]):
    """Render templates.

    Args:
        -I/--input-path (str)  : Path to a input json file or directory.
        -O/--output-path (str) : Path to an output file or directory.
        -td/--tpl-dir (str)    : Path to a templates directory.
        -ext/--extension (str) : Create a file with this extension.
        --show-all (bool)      : If ``True``, show all template filenames in ``tmp-dir``
        --quiet (bool)         : Whether to make the output quiet.

    Note:
        When you run from the command line, execute as follows::
        
        $ render-template -I sample.json
        $ render-template -I dir
        $ render-template --show-all

    Examples:

        - Replace Input file using regular expression:
            .. code-block:: shell

                $ render-template -I sample.json
                - sample.json -> sample.html
                $ render-template -I dir
                Input directory  : dir
                Output directory : dir
                - dir/sample.json -> dir/sample.html
                - dir/subdir/sample.json -> dir/subdir/sample.html

        - Show all json file in ``tpl-dir``
            .. code-block:: shell

                $ render-template --show-all
                Template directory: /Users/iwasakishuto/.pycharmers/cli/render_templates
                * protocols.tpl

        >>> # If you want to try the contents of the template
        >>> from jinja2 import Environment, FileSystemLoader
        >>> from pycharmers.cli._path import PYCHARMERS_CLI_RENDER_TEMPLATES_DIR
        >>> env = Environment(loader=FileSystemLoader(searchpath=PYCHARMERS_CLI_RENDER_TEMPLATES_DIR))
        >>> template = env.get_template("template.tpl")
        >>> print(template.render())
        
    """
    parser = argparse.ArgumentParser(prog="render-template", add_help=True)
    parser.add_argument("-I",   "--input-path",  type=str, required=True, help="Path to input json file or directory.")
    parser.add_argument("-O",   "--output-path", type=str, default=None,  help="Path to output file or directory.")
    parser.add_argument("-td",  "--tmp-dir",     type=str, default=PYCHARMERS_CLI_RENDER_TEMPLATES_DIR, help="Path to templates dir")
    parser.add_argument("-ext", "--extension",   type=str, default=".html", help="Create a file with this extension.")
    parser.add_argument("--remove-pattern",      type=str, default=r".*\/data\/")
    parser.add_argument("--cmap",                type=str, default="tab10", help="Color map name which is supported in ``matplotlib``")
    parser.add_argument("--show-all",     action="store_true", help="If True, show all template filenames in 'tmp-dir'")
    parser.add_argument("--quiet",        action="store_true", help="Whether to make the output quiet")
    parser.add_argument("--date-as-slug", action="store_true", help="Whether to use DATE as a Slug.")
    parser.add_argument("--not-pelican",  action="store_true", help="Whether you want to render template for pelican or not.")
    args = parser.parse_args(argv)

    tmp_dir = args.tmp_dir
    verbose = not args.quiet
    is_pelican = not args.not_pelican
    remove_pattern = args.remove_pattern
    # Show all json file in 'json-dir'
    if args.show_all:
        print(f"Template directory: {toGREEN(tmp_dir)}")
        p = Path(tmp_dir)
        for fn in p.glob("**/*.tpl"):
            print(f"* {toBLUE(os.path.basename(fn))}")
        sys.exit(-1)

    colors_ = ['#{:02x}{:02x}{:02x}'.format(*tuple(rgb.astype(int))) for rgb in np.array(plt.get_cmap(args.cmap).colors)*255]
    env = Environment(loader=FileSystemLoader(searchpath=tmp_dir), extensions=["jinja2.ext.loopcontrols"])
    def render_template(input_path, output_path, date_as_slug=args.date_as_slug, is_pelican=is_pelican):
        if verbose: print(f"- {input_path} -> {output_path}")
        with open(input_path, mode="r") as f_json:
            data = json.load(f_json)
        filename = os.path.splitext(os.path.basename(input_path))[0]

        remove_suffix_num = lambda string : re.sub(pattern=r"(.+?)((?:\d+)?)$", repl=r"\1.html", string=string)
        # Arrange Head for Pelican.
        if is_pelican:
            head = data.get("head", {})
            if date_as_slug or "Slug" not in head:
                head["Slug"] = filename
            if "Date" not in data:
                # filename: YYYY-MM-DD hh:mm
                dates = filename.split("-")
                head["Date"] = "-".join(dates[:3]) + " " + ":".join(dates[-2:])
            # // Arranged Head for Pelican.
            data["head"] = head

        keys = [remove_suffix_num(key)[:-5] for key in data.keys()] # "hoge.html"[:-5] = "hoge"
        add_extra_keys(keys, data)
        content = ""
        for key, vals in data.items():
            vals["colors_"] = colors_
            vals["id_"] = key
            vals["keys_"] = keys
            if ("base_url" in vals) and (not vals["base_url"].endswith("/")): vals["base_url"] += "/"
            template = env.get_template(remove_suffix_num(key))
            content += template.render(**vals) + "\n"
        with open(output_path, mode="w") as f_out:
            f_out.write(content)

    input_path = args.input_path
    ext = args.extension
    if not ext.startswith("."): ext = "." + ext

    # If "input_path" is a file.
    if os.path.isfile(input_path):
        output_path = args.output_path or input_path.replace(".json", ext)
        render_template(input_path, output_path)
    # If "input_path" is a directory
    elif os.path.isdir(input_path):
        if input_path.endswith("/"): input_path = input_path[:-1]
        output_dir = args.output_path
        if output_dir is None: output_dir = input_path
        elif output_dir.endswith("/"): output_dir = output_dir[:-1]
        
        if verbose:
            print(f"Input directory  : {toBLUE(input_path)}")
            print(f"Output directory : {toBLUE(output_dir)}")

        p = Path(input_path)
        for fp in p.glob("**/*.json"):
            fp = str(fp)
            if (remove_pattern is not None) and re.match(pattern=remove_pattern, string=fp): continue
            render_template(fp, fp.replace(input_path, output_dir).replace(".json", ext))
        
        for fp in p.glob("**/*.md.raw"):
            add_title_prefix_for_rawmeta(fp, ext=".raw")

        for fp in p.glob("**/*.nbdata.raw"):
            add_title_prefix_for_rawmeta(fp, ext=".raw")
