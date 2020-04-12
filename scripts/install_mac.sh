#!/usr/bin/env bash

ENV_NAME=avatarify

conda create -y -n $ENV_NAME python=3.8
conda activate $ENV_NAME

# FOMM
git clone https://github.com/alievk/first-order-model.git fomm
pip install -r fomm/requirements.txt

pip install pyyaml
pip install face-alignment