#!/usr/bin/env bash

source scripts/settings.sh

git submodule update --init

# v4l2loopback
echo "--- Installing v4l2loopback (sudo privelege required)"
cd v4l2loopback
make && sudo make install
sudo depmod -a
cd ..

source $(conda info --base)/etc/profile.d/conda.sh
conda create -y -n $CONDA_ENV_NAME python=3.7
conda activate $CONDA_ENV_NAME

pip install face-alignment pyfakewebcam

# FOMM
pip install -r fomm/requirements.txt
pip install requests
