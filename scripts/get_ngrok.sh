#!/usr/bin/env bash

command -v ./ngrok >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo ngrok is not found, installing...
    wget -q -nc https://bin.equinox.io/c/4VmDzA7iaHb/ngrok-stable-linux-amd64.zip
    unzip -qq -n ngrok-stable-linux-amd64.zip
    echo Done!
fi

