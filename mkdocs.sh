#!/bin/bash
# chmod +x mkdocs.sh
# ./mkdocs.sh

function logging() {
  echo -e "\033[0;32m$1\033[0m"
}

function warnings() {
  echo -e "\033[31m$1\033[0m"
}

function whereIam() {
  echo -e "@ \033[07m`pwd`\033[0m"
}

SRC_DIRNAME="src"
DOC_DIRNAME="docs"
MODULE_DIRNAME="pyutils"
CREATED_DIRNAME="_build/html"
HERE=$(cd $(dirname $0);pwd)

logging "cd $HERE"
cd $HERE
whereIam

if [ -d $DOC_DIRNAME ]; then
  warnings "Delete old $DOC_DIRNAME directory."
  rm -rf $DOC_DIRNAME
fi

logging "$ sphinx-apidoc -f -o $SRC_DIRNAME $MODULE_DIRNAME"
sphinx-apidoc -f -o $SRC_DIRNAME $MODULE_DIRNAME

logging "cd $SRC_DIRNAME"
cd $SRC_DIRNAME
whereIam

logging "make html"
make html
logging "mv $CREATED_DIRNAME ../$DOC_DIRNAME"
mv $CREATED_DIRNAME ../$DOC_DIRNAME
