#!/usr/bin/env bash

# check prerequisites
command -v conda >/dev/null 2>&1 || { echo >&2 "conda not found. Please refer to the README and install Miniconda."; exit 1; }
command -v git >/dev/null 2>&1 || { echo >&2 "git not found. Please refer to the README and install Git."; exit 1; }

source scripts/settings.sh

# v4l2loopback
if [[ ! $@ =~ "no-vcam" ]]; then
    rm -rf v4l2loopback 2> /dev/null
    git clone https://github.com/alievk/v4l2loopback.git
    echo "--- Installing v4l2loopback (sudo privelege required)"
    cd v4l2loopback
    make && sudo make install
    sudo depmod -a
    cd ..
fi

source $(conda info --base)/etc/profile.d/conda.sh
conda create -y -n $CONDA_ENV_NAME python=3.7
conda activate $CONDA_ENV_NAME

conda install -y pytorch==1.0.0 torchvision==0.2.1 cuda100 -c pytorch
conda install -y python-blosc==1.7.0 -c conda-forge

# FOMM
rm -rf fomm 2> /dev/null
git clone https://github.com/alievk/first-order-model.git fomm

pip install -r requirements.txt
