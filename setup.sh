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

conda run -n tree cmake -B $REPO_DIR/build $REPO_DIR
conda run -n tree cmake --build $REPO_DIR/build 

SO_PATH=($REPO_DIR/build/tree_core*.so)

ln -sf ${SO_PATH[0]} $REPO_DIR/blender/

echo "Activate the tree environment (conda activate tree), if activated deactivate (conda deactivate), and activate again"
