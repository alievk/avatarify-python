#!/usr/bin/env bash
echo "--- check prerequisites"
# check prerequisites
command -v pip3 >/dev/null 2>&1 || { echo >&2 "pip3 not found. Please refer to the README and install Pip."; exit 1; }
command -v git >/dev/null 2>&1 || { echo >&2 "git not found. Please refer to the README and install Git."; exit 1; }

source scripts/settings.sh

echo "--- v4l2loopback"
# v4l2loopback
rm -rf v4l2loopback 2> /dev/null
git clone https://github.com/alievk/v4l2loopback.git
echo "--- Installing v4l2loopback (sudo privelege required)"
cd v4l2loopback
make && sudo make install
sudo depmod -a
cd ..

echo "--- FOMM"
# FOMM
rm -rf fomm 2> /dev/null
git clone https://github.com/alievk/first-order-model.git fomm
echo "--- pip install"
pip3 install -r requirements_jetson.txt
