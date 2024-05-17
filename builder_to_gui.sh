#!/bin/bash

# make img folder in GUI
mkdir -p ./GUI/img
# copy image builder files
cp IMAGE_BUILDER/__init__.py GUI/img/__init__.py
cp IMAGE_BUILDER/podmanager.py GUI/img/podmanager.py
cp IMAGE_BUILDER/requirements.txt GUI/img/pod_req.txt
cp IMAGE_BUILDER/kaniko.yml GUI/img/kaniko.yml


