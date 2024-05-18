#!/bin/bash

# make img folder in GUI
mkdir -p ./GUI/UI/frontend/img
# copy image builder files
cp IMAGE_BUILDER/__init__.py GUI/UI/frontend/img/__init__.py
cp IMAGE_BUILDER/podmanager.py GUI/UI/frontend/img/podmanager.py
cp IMAGE_BUILDER/requirements.txt GUI/UI/frontend/img/pod_req.txt
cp IMAGE_BUILDER/kaniko.yml GUI/UI/frontend/img/kaniko.yml


