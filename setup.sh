#!/bin/bash

if ! conda env list | grep -q "^tree" ; then
   conda env create -f environment.yml 
fi

REPO_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

conda env config vars set PYTHONPATH=$REPO_DIR/build -n tree

if [ -z "$BLENDER_PATH" ]; then
   read -p "Enter Blender path: " BLENDER_PATH
   conda env config vars set BLENDER_PATH=$BLENDER_PATH -n tree
fi

echo "Activate the tree environment (conda activate tree), if activated deactivate (conda deactivate), and activate again"
