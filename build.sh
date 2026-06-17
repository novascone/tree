#!/bin/bash

REPO_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

if [ "$1" = "--full" ]; then
   rm -rf $REPO_DIR/build
   conda run -n tree cmake -B $REPO_DIR/build $REPO_DIR
fi

conda run -n tree cmake --build $REPO_DIR/build 

SO_PATH=($REPO_DIR/build/tree_core*.so)

cp ${SO_PATH[0]} $REPO_DIR/blender/

EXT_DIRS=(~/.config/blender/*/extensions/user_default/tree)

if [ -d "${EXT_DIRS[0]}" ]; then
   cp ${SO_PATH[0]} "${EXT_DIRS[0]}/"
fi

conda run -n tree bash -c "cd $REPO_DIR/blender && \$BLENDER_PATH/blender --command extension build"

