#!/bin/bash

ENV_NAME=avatarify

conda create -y -n $ENV_NAME python=3.8
conda activate $ENV_NAME

conda install pytorch torchvision cudatoolkit=10.1 -c pytorch
conda install -c 1adrianb face_alignment

# FOMM
git clone https://github.com/alievk/first-order-model.git fomm
pip install -r fomm/requirements.txt
