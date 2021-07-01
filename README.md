# Python-Charmers

[![header](https://github.com/iwasakishuto/Python-Charmers/blob/master/image/header.png?raw=true)](https://github.com/iwasakishuto/Python-Charmers)
[![PyPI version](https://badge.fury.io/py/Python-Charmers.svg)](https://pypi.org/project/Python-Charmers/)
[![GitHub version](https://badge.fury.io/gh/iwasakishuto%2FPython-Charmers.svg)](https://github.com/iwasakishuto/Python-Charmers)
[![Execute Python-Charmers](https://github.com/iwasakishuto/Python-Charmers/actions/workflows/execute_python_package.yml/badge.svg)](https://github.com/iwasakishuto/Python-Charmers/actions/workflows/execute_python_package.yml)
[![Upload to PyPI with Poetry](https://github.com/iwasakishuto/Python-Charmers/actions/workflows/upload_python_package_poetry.yml/badge.svg)](https://github.com/iwasakishuto/Python-Charmers/actions/workflows/upload_python_package_poetry.yml)
[![license](https://img.shields.io/github/license/mashape/apistatus.svg?maxAge=2592000)](https://github.com/iwasakishuto/Python-Charmers/blob/master/LICENSE)

A collection of useful python programs.

## Installation

1. Install **MySQL**
	- **Debian/Ubuntu**
		```sh
		$ sudo apt-get install python3-dev default-libmysqlclient-dev build-essential
		```
	- **Red Hat/Cent OS**
		```sh
		% sudo yum install python3-devel mysql-devel
		```
	- **macOS**
		```sh
		# Install MySQL server
		$ brew install mysql
		# If you don't want to install MySQL server, you can use mysql-client instead:
		$ brew install mysql-client
		$ echo 'export PATH="/usr/local/opt/mysql-client/bin:$PATH"' >> ~/.zprofile
		$ export PATH="/usr/local/opt/mysql-client/bin:$PATH"
		```
2. Install **`Python-Charmers`** (There are two ways to install):
	-  Create an environment for Python-Charmers using [Pyenv](https://github.com/pyenv/pyenv) and [Poetry](https://python-poetry.org/) **(recommended)**
		```sh
		$ pyenv install 3.8.9
		$ pyenv local 3.8.9
		$ python -V
		Python 3.8.9
		$ poetry install
		```
	-  Install in a specific environment
		-  Install from PyPI:
			```sh
			$ sudo pip install Python-Charmers
			```
		-  Alternatively: install PyGuitar from the GitHub source:
			```sh            
			$ git clone https://github.com/iwasakishuto/Python-Charmers.git
			# If you want to use the latest version (under development)
			$ git clone -b develop https://github.com/iwasakishuto/Python-Charmers.git
			$ cd Python-Charmers
			$ sudo python setup.py install
			```
3. Install **driver** for `selenium`:
**`Selenium`** requires a driver to interface with the chosen browser, so please visit the [documentation](https://selenium-python.readthedocs.io/installation.html#drivers) to install it.
	```sh
	# Example: Chrome
	# visit "chrome://settings/help" to check your chrome version.
	# visit "https://chromedriver.chromium.org/downloads" to check <Suitable.Driver.Version> for your chrome.
	$ wget https://chromedriver.storage.googleapis.com/<Suitable.Driver.Version>/chromedriver_mac64.zip
	$ unzip chromedriver_mac64.zip
	$ mv chromedriver /usr/local/bin/chromedriver
	$ chmod +x /usr/local/bin/chromedriver
	```

### Pyenv + Poetry

- [Pyenv](https://github.com/pyenv/pyenv) is a python installation manager.
- [Poetry](https://python-poetry.org/) is a packaging and dependency manager.

I recommend you to use these tools to **avoid the chaos** of the python environment. See other sites for how to install these tools.

```sh
$ pyenv install 3.8.9
$ pyenv local 3.8.9
$ python -V
Python 3.8.9
$ poetry install 
$ poetry run pycharmers-show
$ poetry run book2img
```

## CLI

**CLI** is a command line program that accepts text input to execute operating system functions.

```sh
# If you use Poetry to set up the environment.
$ poetry run pycharmers-show
|       command       |                         path                         |
|:-------------------:|:-----------------------------------------------------|
|            book2img | pycharmers.cli.book2img:book2img                     |
|         cv-cascades | pycharmers.cli.cvCascades:cvCascades                 |
|               :     |              :                                       |
|            tweetile | pycharmers.cli.tweetile:tweetile                     |
|           video2gif | pycharmers.cli.video2gif:video2gif                   |
```

|                                                                              command                                                                               |                                   description                                                                                                             |
|:------------------------------------------------------------------------------------------------------------------------------------------------------------------:|:----------------------------------------------------------------------------------------------------------------------------------------------------------|
|                                         [`book2img`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.book2img.html#pycharmers.cli.book2img.book2img) | Convert Book into Sequential Images.                                                                                                                      |
|                                [`cv-cascades`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.cvCascades.html#pycharmers.cli.cvCascades.cvCascades) | Control the OpenCV cascade Examples.                                                                                                                      |
|               [`cv-paper-scanner`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.cvPaperScanner.html#pycharmers.cli.cvPaperScanner.cvPaperScanner) | Paper Scanner using OpenCV.                                                                                                                               |
|               [`cv-pencil-sketch`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.cvPencilSketch.html#pycharmers.cli.cvPencilSketch.cvPencilSketch) | Convert the image like a pencil drawing.                                                                                                                  |
|                                        [`cv-window`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.cvWindow.html#pycharmers.cli.cvWindow.cvWindow) | Use [`cvWindow`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.opencv.windows.html#pycharmers.opencv.windows.cvWindow) to control frames.     |
|     [`form-auto-fill-in`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.form_auto_fill_in.html#pycharmers.cli.form_auto_fill_in.form_auto_fill_in) | Auto fill in your form using your saved information (or answer on the spot).                                                                              |
|             [`jupyter-arrange`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.jupyter_arrange.html#pycharmers.cli.jupyter_arrange.jupyter_arrange) | Arrange Jupyter Notebook.                                                                                                                                 |
|                             [`openBrowser`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.openBrowser.html#pycharmers.cli.openBrowser.openBrowser) | Display url using the default browser.                                                                                                                    |
|                                             [`pdfmine`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.pdfmine.html#pycharmers.cli.pdfmine.pdfmine) | Analyze PDF and extract various elements.                                                                                                                 |
| [`regexp-replacement`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.regexp_replacement.html#pycharmers.cli.regexp_replacement.regexp_replacement) | String replacement in a file using regular expression                                                                                                     |
|             [`render-template`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.render_template.html#pycharmers.cli.render_template.render_template) | Render templates.                                                                                                                                         |
|           [`requirements-create`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.requirements.html#pycharmers.cli.requirements.requirements_create) | Create a ``requirements.text``                                                                                                                            |
|                             [`revise_text`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.revise_text.html#pycharmers.cli.revise_text.revise_text) | Revise word file.                                                                                                                                         |
|                        [`pycharmers-show`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.show.html#pycharmers.cli.show.show_command_line_programs) | Show all Python-Charmers's command line programs.                                                                                                         |
|                                         [`tweetile`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.tweetile.html#pycharmers.cli.tweetile.tweetile) | Divide one image into three so that you can tweet beautifully.                                                                                            |
|                 [`video_of_lyric`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.video_of_lyric.html#pycharmers.cli.video_of_lyric.video_of_lyric) | Create a lyric Video.                                                                                                                                     |
|             [`video_of_typing`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.video_of_typing.html#pycharmers.cli.video_of_typing.video_of_typing) | Create a typing video. Before using this program, please do the following things                                                                          |
|                                     [`video2gif`](https://iwasakishuto.github.io/Python-Charmers/pycharmers.cli.video2gif.html#pycharmers.cli.video2gif.video2gif) | Convert Video into Gif.                                                                                                                                   |