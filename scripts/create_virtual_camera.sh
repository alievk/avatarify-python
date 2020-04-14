#!/usr/bin/env bash

source scripts/settings.sh

FILE=/dev/video$CAMID_VIRT
if [[ ! -w "$FILE" ]]; then
    echo "Creating virtual camera $FILE (sudo privelege required)"
    sudo modprobe v4l2loopback exclusive_caps=1 video_nr=$CAMID_VIRT card_label="avatarify"
fi
