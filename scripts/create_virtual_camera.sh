#!/usr/bin/env bash

source scripts/settings.sh

FILE=/dev/video$CAMID_VIRT
if [[ ! -w "$FILE" ]]; then
    echo "Creating virtual camera $FILE (sudo privelege required)"
    sudo modprobe v4l2loopback exclusive_caps=1 video_nr=$CAMID_VIRT card_label="avatarify"
    #sudo v4l2-ctl -d /dev/video$CAMID_VIRT -c timeout=1000
fi
