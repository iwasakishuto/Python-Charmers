#coding: utf-8
import os
import re
import sys
import json
import argparse
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from ._path import PYCHARMERS_CLI_RENDER_TEMPLATES_DIR
from ..utils._colorings import toBLUE, toGREEN

def render_template(argv=sys.argv[1:]):
    """String replacement using regular expression

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
    """
    parser = argparse.ArgumentParser(prog="render-template", add_help=True)
    parser.add_argument("-I",   "--input-path",  type=str, required=True, help="Path to input json file or directory.")
    parser.add_argument("-O",   "--output-path", type=str, default=None,  help="Path to output file or directory.")
    parser.add_argument("-td",  "--tmp-dir",     type=str, default=PYCHARMERS_CLI_RENDER_TEMPLATES_DIR, help="Path to templates dir")
    parser.add_argument("-ext", "--extension",   type=str, default=".html", help="Create a file with this extension.")
    parser.add_argument("--show-all",     action="store_true", help="If True, show all template filenames in 'tmp-dir'")
    parser.add_argument("--quiet",        action="store_true", help="Whether to make the output quiet")
    parser.add_argument("--date-as-slug", action="store_true", help="Whether to use DATE as a Slug.")
    args = parser.parse_args(argv)

    tmp_dir = args.tmp_dir
    verbose = not args.quiet
    # Show all json file in 'json-dir'
    if args.show_all:
        print(f"Template directory: {toGREEN(tmp_dir)}")
        p = Path(tmp_dir)
        for fn in p.glob("**/*.tpl"):
            print(f"* {toBLUE(os.path.basename(fn))}")
        sys.exit(-1)

    env = Environment(loader=FileSystemLoader(searchpath=tmp_dir))
    def render_template(input_path, output_path, date_as_slug=args.date_as_slug):
        if verbose: print(f"- {input_path} -> {output_path}")
        with open(input_path, mode="r") as f_json:
            data = json.load(f_json)
        filename = os.path.splitext(os.path.basename(input_path))[0]

        # Arrange Head for Pelican.
        head = data.get("head", {})
        if date_as_slug or "Slug" not in head:
            head["Slug"] = filename
        if "Date" not in data:
            # filename: YYYY-MM-DD hh:mm
            dates = filename.split("-")
            head["Date"] = "-".join(dates[:3]) + " " + ":".join(dates[-2:])
        data["head"] = head

        content = ""
        for key, vals in data.items():
            vals["id_"] = key
            if ("base_url" in vals) and (not vals["base_url"].endswith("/")): vals["base_url"] += "/"
            template = env.get_template(re.sub(pattern=r"(.+?)((?:\d+)?)$", repl=r"\1.html", string=key))
            content += template.render(**vals)        
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
            render_template(fp, fp.replace(input_path, output_dir).replace(".json", ext))