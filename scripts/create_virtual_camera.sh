#!/usr/bin/env bash

source scripts/settings.sh

echo 'Creating virtual camera (this may require sudo password once after reboot)'
sudo modprobe v4l2loopback exclusive_caps=1 video_nr=$CAMID_VIRT card_label="avatarify"
