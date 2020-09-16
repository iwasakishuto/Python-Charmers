# coding: utf-8
import os
import setuptools
import pycharmers

DESCRIPTION = "A collection of useful python programs."

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    LONG_DESCRIPTION = f.read()
with open(os.path.join(here,"requirements.txt"), mode="r") as f:
    INSTALL_REQUIRES = [line.rstrip("\n") for line in f.readlines() if line[0]!=("#")]
with open(os.path.join(here,"console_scripts.txt"), mode="r") as f:
    CONSOLE_SCRIPTS = [line.rstrip("\n") for line in f.readlines() if line[0]!=("#")]

def setup_package():
    metadata = dict(
        name="Python-Charmers",
        version=pycharmers.__version__,
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        long_description_content_type="text/markdown",
        author="Shuto Iwasaki",
        author_email="cabernet.rock@gmail.com",
        license="MIT",
        project_urls={
            "Bug Reports" : "https://github.com/iwasakishuto/PythonUtils/issues",
            "Source Code" : "https://github.com/iwasakishuto/PythonUtils",
            "Say Thanks!" : "https://twitter.com/cabernet_rock",
        },
        packages=setuptools.find_packages(),
        python_requires=">=3.6",
        install_requires=INSTALL_REQUIRES,
        extras_require={
          "tests": ["pytest"],
        },
        classifiers=[
            "Development Status :: 1 - Planning",
            "Environment :: Console",
            "Intended Audience :: Other Audience",
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.8",
            "Topic :: Software Development :: Libraries :: Python Modules",
        ],
        entry_points = {
            "console_scripts": CONSOLE_SCRIPTS,
        },
    )
    setuptools.setup(**metadata)

if __name__ == "__main__":
    setup_package()