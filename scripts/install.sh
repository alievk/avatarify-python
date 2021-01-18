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

conda install -y numpy==1.19.0 scikit-image python-blosc==1.7.0 -c conda-forge
conda install -y pytorch==1.7.1 torchvision cudatoolkit=11.0 -c pytorch

# FOMM
rm -rf fomm 2> /dev/null
git clone https://github.com/alievk/first-order-model.git fomm

pip install -r requirements.txt
