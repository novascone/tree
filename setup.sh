#!/bin/bash

if ! conda env list | grep -q "^tree" ; then
   conda env create -f environment.yml 
fi

if [ -z "$BLENDER_PATH" ]; then
   read -p "Enter Blender path: " BLENDER_PATH
   sed -i "s|BLENDER_PATH:.*|BLENDER_PATH: $BLENDER_PATH|" environment.yml  
fi

PYTHON_BIN=($BLENDER_PATH/*/python/bin/python3*)
VERSION_STRING=$(${PYTHON_BIN[0]} --version)
VERSION=$(echo $VERSION_STRING | awk '{print $2}' | cut -d. -f1,2)

echo "Activate the tree environment: conda activate tree"
