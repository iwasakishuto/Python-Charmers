# coding: utf-8
import os
import sys
import pytest
from data import TestData
import warnings
try:
    from pycharmers.utils._warnings import PythonCharmersImprementationWarning
except ModuleNotFoundError:
    here     = os.path.abspath(os.path.dirname(__file__))
    REPO_DIR = os.path.dirname(here)
    sys.path.append(REPO_DIR)
    print(f"You didn't install 'Python-Charmers', so add {REPO_DIR} to search path for modules.")
    from pycharmers.utils._warnings import PythonCharmersImprementationWarning

def pytest_addoption(parser):
    parser.addoption("--pycharmers-warnings", choices=["error", "ignore", "always", "default", "module", "once"], default="ignore")

def pytest_configure(config):
    action = config.getoption("pycharmers_warnings")
    warnings.simplefilter(action, category=PythonCharmersImprementationWarning)
    warnings.simplefilter(action, category=FutureWarning)

@pytest.fixture
def db():
    database = TestData()
    return database