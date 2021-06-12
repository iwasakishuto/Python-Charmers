# coding: utf-8
import os
import sys
import json
import argparse

from pathlib import Path
from typing import Any,Dict

def reorder_jupyter(jupyter_dict:Dict[str,Any])->Dict[str,Any]:
    """Reorder the execution count in Jupyter Notebook (``.ipynb``)

    Args:
        jupyter_dict (Dict[str,Any]): The contents of the jupyter notebook file (``.ipynb``).

    Returns:
        Dict[str,Any]: The reordered contents of the jupyter notebook file.
    """
    N = sum([1 for cell in jupyter_dict['cells'] if 'execution_count' in cell])
    num = 0
    for cell in jupyter_dict['cells']:
        if 'execution_count' in cell:
            num+=1
            cell['execution_count'] = num
            if 'outputs' in cell:
                outputs = cell['outputs']
                for output in outputs:
                    if 'execution_count' in output:
                        cell['outputs'][0]['execution_count']=num
                        # output['execution_count'] = num
            if num==N-1:
                break
    return jupyter_dict


name2method = {
    "reorder" : reorder_jupyter,
}

def jupyter_arrange(argv=sys.argv[1:]):
    """Arrange Jupyter Notebook.

    Args:
        -I/-in/--input-jupyter (str)   : The path to ``input_jupyter.ipynb``.
        -O/-out/--output-jupyter (str) : The path to ``output_jupyter.ipynb``.
        -M/--method (str)              :　Which method to apply?
    
    NOTE:
        When you run from the command line, execute as follows::

            $ jupyter-arrange -I path/to/input.ipynb -O path/to/output.ipynb -M reorder
    """
    parser = argparse.ArgumentParser(prog="jupyter-arrange", description="Arrange jupyter notebook.", add_help=True)
    parser.add_argument("-I", "-in",  "--input-jupyter",  type=str, required=True, help="The path to input_jupyter.ipynb")
    parser.add_argument("-O", "-out", "--output-jupyter", type=str, default=None,  help="The path to output_jupyter.ipynb")
    parser.add_argument("-M", "--method", choices=list(name2method.keys()), default="reorder", help="Which method to apply?")
    args = parser.parse_args()

    input_jupyter = args.input_jupyter
    output_jupyter = args.output_jupyter
    method = args.method
    if output_jupyter is None:
        output_jupyter = f"_{method}".join(os.path.splitext(input_jupyter))
    
    # Read jupyter file.
    with open(input_jupyter, mode="r") as input_file:
        jupyter_dict = json.load(input_file)
    # Arrange
    jupyter_dict = name2method[method](jupyter_dict)
    # Write jupyter file.
    with open(output_jupyter, mode="w") as output_file:
        json.dump(jupyter_dict, output_file)