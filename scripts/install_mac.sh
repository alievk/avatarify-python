#!/usr/bin/env bash

ENV_NAME=avatarify

conda create -y -n $ENV_NAME python=3.7

source $(conda info --base)/etc/profile.d/conda.sh
conda activate $ENV_NAME

# FOMM
rm -rf fomm 2> /dev/null
git clone https://github.com/alievk/first-order-model.git fomm

pip install -r requirements.txt
