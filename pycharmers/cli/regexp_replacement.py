#coding: utf-8
import os
import re
import sys
import json
import argparse
from pathlib import Path

from ._path import PYCHARMERS_CLI_REGEXP_REPLACEMENT_DIR
from ..utils._colorings import toBLUE, toGREEN
from ..utils.generic_utils import pycat

def regexp_replacement(argv=sys.argv[1:]):
    """String replacement using regular expression

    - ``.json`` path can be specified by "``json-dir`` / ``json-file``" or "``json-path``"
    - output file path can be specified by "``output-path``" or "``input-path`` + ``suffix``"

    Args:
        -I/--input-path (str)  : Path/to/input file.
        -O/--output-path (str) : Path/to/output file.
        -jd/--json-dir (str)   : Path/to/json directory.
        -jf/--json-file (str)  : File name in ``json-dir``.
        -jp/--json-path (str)  : Path/to/json file.
        -suf/--suffix (str)    : Suffix of output filename.
        -ext/--extension (str) : When 'input-path' is directory, only file in 'input-path' with this extension will be replaced.
        --show-all (bool)      : If ``True``, show all json file descriptions in ``json-dir``
        --show (bool)          : If ``True``, show the content of a specified json file.

    Note:
        When you run from the command line, execute as follows::
        
        $ regexp_replacement -I sample.md -jf sample.json
        $ regexp_replacement --show-all
        $ regexp_replacement -jf sample.json --show

    Examples:

        - Replace Input file using regular expression.
            .. code-block:: shell

                $ regexp-replacement -I sample.md -jf sample.json
                    Json   file : /Users/iwasakishuto/.pycharmers/cli/regexp_replacement/labbooks.json
                    Input  file : sample.md
                    Output file : sample.md
                $ regexp-replacement -I sample.md -jf sample.json -suf suffix
                    Json: /Users/iwasakishuto/.pycharmers/cli/regexp_replacement/labbooks.json
                    Input path : sample.md
                    Output path: sample_suffix.md

        - Show all json file in ``json-dir``

            .. code-block:: shell

                $ regexp-replacement --show-all
                Json directory: /Users/iwasakishuto/.pycharmers/cli/regexp_replacement
                * sample.json: Sample Json

        - Show the content of the file at ``json-path``

            .. code-block:: shell

                $ regexp-replacement -jf sample.json --show
                Json:  /Users/iwasakishuto/.pycharmers/cli/regexp_replacement/sample.json
                {
                    "description" : "Sample Json",
                    "patterns" : [
                        ["`(.*?)`", "<span class=\"code\">\\1</span>"],
                        ["+(.*?)+", "<span class=\"strong\">\\1</span>"]
                    ]
                }
    """
    parser = argparse.ArgumentParser(prog="regexp-replace", add_help=True)
    parser.add_argument("-I",  "--input-path",  type=str, default=None, help="Path/to/input file.")
    parser.add_argument("-O",  "--output-path", type=str, default=None, help="Path/to/output file.")
    parser.add_argument("-jd", "--json-dir",    type=str, default=PYCHARMERS_CLI_REGEXP_REPLACEMENT_DIR, help="Path to JSON dir.")
    parser.add_argument("-jf", "--json-file",   type=str, default=None, help="Path to JSON file from 'json-dir'")
    parser.add_argument("-jp", "--json-path",   type=str, default=None, help="Path to JSON file.")
    parser.add_argument("-suf", "--suffix",     type=str, default="",   help="Suffix of output filename.")
    parser.add_argument("-ext", "--extension",  type=str, default="",   help="When 'input-path' is directory, only file in 'input-path' with this extension will be replaced.")
    parser.add_argument("--show-all", action="store_true", help="If True, show all json file descriptions in 'json-dir'")
    parser.add_argument("--show",     action="store_true", help="If True, show the content of a specified json file.")
    args = parser.parse_args(argv)

    # Show all json file in 'json-dir'
    if args.show_all:
        json_dir = args.json_dir
        print(f"Json directory: {toGREEN(json_dir)}")
        p = Path(json_dir)
        for fn in p.glob("**/*.json"):
            with open(fn.absolute()) as f:
                print(f"* {toBLUE(fn.name)}: {json.load(f).get('description')}")
        sys.exit(-1)

    # Show the content of the file at `json-path`
    json_path = args.json_path or os.path.join(args.json_dir, args.json_file)
    print(f"Json: {toBLUE(json_path)}")
    if args.show:
        pycat(json_path)
        sys.exit(-1)

    # Get the contents from json and create a replacement functions.
    with open(json_path, mode="r") as f_json:
        data = json.load(f_json).get("patterns", [])

    # Replace Strings.
    def replace_str(string):
        for pat, repl in data:
            string = re.sub(pattern=rf"{pat}", repl=rf"{repl}", string=string)
        return string
    # Replace File contents.
    def replace_file(input_path, output_path):
        with open(input_path, mode="r") as f_in:
            readlines = f_in.readlines()
        with open(output_path, mode="w") as f_out:
            f_out.writelines([replace_str(line) for line in readlines])

    def add_suffix(path, suffix, sep="."):
        *fp, ext = path.split(sep)
        return f"{sep.join(fp)}_{suffix}{sep}{ext}"

    input_path = args.input_path
    suffix = args.suffix
    if os.path.isfile(input_path):
        output_path = args.output_path or add_suffix(input_path,suffix)
        print(f"Input path : {toBLUE(input_path)}")
        print(f"Output path: {toBLUE(output_path)}")
        replace_file(input_path, output_path)
    elif os.path.isdir(input_path):
        if input_path.endswith("/"): input_path = input_path[:-1]
        output_dir = args.output_path
        if output_dir is None:
            in2out = add_suffix
        else:
            if output_dir.endswith("/"): output_dir = output_dir[:-1]
            in2out = lambda path, suffix : path.replace(input_path, output_dir)
        
        print(f"Input dir : {toBLUE(input_path)}")
        print(f"Output dir: {toBLUE(output_path)}")
        ext = args.extension

        p = Path(input_path)
        for fp in p.glob(f"**/*{ext}"):
            fp = str(fp)
            replace_file(fp, in2out(fp, suffix))