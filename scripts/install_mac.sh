#!/usr/bin/env bash

source scripts/settings.sh

source $(conda info --base)/etc/profile.d/conda.sh
conda create -y -n $CONDA_ENV_NAME python=3.7
conda activate $CONDA_ENV_NAME

# FOMM
rm -rf fomm 2> /dev/null
git clone https://github.com/alievk/first-order-model.git fomm

conda install -y pytorch==1.0.0 torchvision==0.2.1 -c pytorch
conda install -y matplotlib==2.2.2
pip install -r requirements.txt
