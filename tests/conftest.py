# coding: utf-8
import os
import sys
import pytest
from data import TestData
import warnings
try:
    from gummy.utils._warnings import PythonUtilsImprementationWarning
except ModuleNotFoundError:
    here     = os.path.abspath(os.path.dirname(__file__))
    REPO_DIR = os.path.dirname(here)
    sys.path.append(REPO_DIR)
    print(f"You didn't install 'PythonUtils', so add {REPO_DIR} to search path for modules.")
    from lib.utils._warnings import PythonUtilsImprementationWarning

def pytest_addoption(parser):
    parser.addoption("--pyutils-warnings", choices=["error", "ignore", "always", "default", "module", "once"], default="ignore")

def pytest_configure(config):
    action = config.getoption("pyutils_warnings")
    warnings.simplefilter(action, category=PythonUtilsImprementationWarning)

@pytest.fixture
def db():
    database = TestData()
    return database