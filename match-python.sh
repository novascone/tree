#!/bin/bash

if [ -z "$BLENDER_PATH" ]; then
   read -p "Enter Blender path: " BLENDER_PATH
   conda env config vars set BLENDER_PATH=$BLENDER_PATH -n tree
fi

PYTHON_BIN=($BLENDER_PATH/*/python/bin/python3*)
VERSION_STRING=$(${PYTHON_BIN[0]} --version)
VERSION=$(echo $VERSION_STRING | awk '{print $2}' | cut -d. -f1,2)

if [ "$CONDA_DEFAULT_ENV" != "tree" ]; then
   echo "Activate the tree environment: conda activate tree"
   exit 1
fi

conda install python=$VERSION
