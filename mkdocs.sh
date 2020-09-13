#!/bin/bash
# chmod +x mkdocs.sh
# ./mkdocs.sh

SRC_DIRNAME="src"
DOC_DIRNAME="docs"
CREATED_DIRNAME="_build"

here=$(cd $(dirname $0);pwd) 
cd $here

if [ -d $DOC_DIRNAME ]; then
  echo "Delete $DOC_DIRNAME directory."
  rm -rf $DOC_DIRNAME
fi

cd $SRC_DIRNAME
make html
mv $CREATED_DIRNAME $DOC_DIRNAME
mv $DOC_DIRNAME ../$DOC_DIRNAME