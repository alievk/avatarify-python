#!/usr/bin/env bash

ENV_NAME=avatarify

conda create -y -n $ENV_NAME python=3.8
conda activate $ENV_NAME

# FOMM
git clone https://github.com/alievk/first-order-model.git fomm
pip install -r fomm/requirements.txt

# v4l2loopback
git clone https://github.com/umlaeute/v4l2loopback
cd v4l2loopback
make && sudo make install
sudo depmod -a
#sudo insmod v4l2loopback.ko exclusive_caps=1 video_nr=1 card_label="avatarify"
sudo modprobe v4l2loopback exclusive_caps=1 video_nr=1 card_label="avatarify"
cd ..
