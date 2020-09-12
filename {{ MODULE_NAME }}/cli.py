# coding: utf-8
import sys
import argparse
from .utils.generic_utils import MonoParamProcessor

def func(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(prog="command-name", add_help=True)
    parser.add_argument("-P", "--params", default={}, action=MonoParamProcessor, help="Specify the kwargs. You can specify by -P username=USERNAME -P password=PASSWORD")
    args = parser.parse_args(argv)
