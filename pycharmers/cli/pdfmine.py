#coding: utf-8
import io
import os
import sys
import fitz
import camelot
import argparse
from PIL import Image

from ..utils._colorings import toBLUE, toGREEN, toRED
from ..utils._path import _makedirs
from ..utils.generic_utils import formatted_enumerator
from ..utils.print_utils import pretty_3quote

SUPPORTED_TARGETS = ["img", "image", "table"]

def pdfmine(argv=sys.argv[1:]):
    """Analyze PDF and extract various elements.

    Args:
        path (str)             : Path/to/input PDF file.
        -O/--output-path (str) : Path/to/output directory.
        -T/--target (str)      : Target to extract.
        --quiet (bool)         : Whether to make the output quiet.

    Note:
        When you run from the command line, execute as follows::
        
        $ pdfmine -I sample.pdf -T img
    """
    parser = argparse.ArgumentParser(prog="pdfmine", add_help=True)
    parser.add_argument("path", type=str, help="Path/to/input PDF file.")
    parser.add_argument("-O", "--output-dir",  type=str, default=None, help="Path/to/output directory.")
    parser.add_argument("-T", "--target",      type=str, choices=SUPPORTED_TARGETS, help="Target to extract.")
    parser.add_argument("--quiet",    action="store_true", help="Whether to make the output quiet")
    args = parser.parse_args(argv)

    input_path = args.path
    output_dir = args.output_dir or os.path.splitext(input_path)[0]
    _makedirs(output_dir)
    target = args.target
    verbose = not args.quiet

    if verbose: 
        print(*pretty_3quote(f"""
        [pdfmine]
        * Input PDF file is at {toBLUE(input_path)}
        * Extracted data will be saved at {toBLUE(output_dir)}
        * Extraction target is {toGREEN(target)}
        """))

    if target in ["img", "image"]:
        pdf_file = fitz.open(input_path)
        pdf_gen = formatted_enumerator(pdf_file, start=1)
        for page_idx, page in pdf_gen:
            img_list = page.getImageList()
            img_gen = formatted_enumerator(img_list, start=1)
            if verbose:
                if img_gen.total>0:
                    print(f"[+] Found a total of {toGREEN(img_gen.total)} images in {page_idx}")
                else:
                    print(f"[!] No images found on page {page_idx}")
            for img_idx, img in formatted_enumerator(img_list, start=1):
                print("    - ", end="")
                xref = img[0]
                base_image = pdf_file.extractImage(xref=xref)
                fp = os.path.join(output_dir, f"p{page_idx}_{img_idx}.{base_image['ext']}")
                try:
                    with open(fp, "wb"):
                        Image.open(io.BytesIO(base_image["image"])).save(fp)
                    msg = toGREEN("saved")
                except Exception as e:
                    msg = toRED(e)
                print(f"\033[1F\033[{28+len(str(xref))}G {msg}")
                
    elif target == "table":
        tables = camelot.read_pdf(input_path)
        table_gen = formatted_enumerator(tables, start=1)
        print(f"Found a total of {table_gen.total} tables.")
        for table_idx,table in table_gen:
            table.to_csv(os.path.join(output_dir, table_idx+".csv"))
