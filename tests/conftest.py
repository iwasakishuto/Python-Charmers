# coding: utf-8
import os
import sys
import pytest
from data import TestData
import warnings
try:
    from gummy.utils._warnings import {{ PACKAGE_NAME_CODE }}ImprementationWarning
except ModuleNotFoundError:
    here     = os.path.abspath(os.path.dirname(__file__))
    REPO_DIR = os.path.dirname(here)
    sys.path.append(REPO_DIR)
    print(f"You didn't install '{{ REPOSITORY_NAME }}', so add {REPO_DIR} to search path for modules.")
    from lib.utils._warnings import {{ PACKAGE_NAME_CODE }}ImprementationWarning

def pytest_addoption(parser):
    parser.addoption("--{{ MODULE_NAME }}-warnings", choices=["error", "ignore", "always", "default", "module", "once"], default="ignore")

def pytest_configure(config):
    action = config.getoption("{{ MODULE_NAME }}_warnings")
    warnings.simplefilter(action, category={{ PACKAGE_NAME_CODE }}ImprementationWarning)

@pytest.fixture
def db():
    database = TestData()
    return database