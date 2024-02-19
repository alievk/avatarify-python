#!/usr/bin/env bash

# Check if ngrok is installed
command -v ngrok >/dev/null 2>&1
if [[ $? -ne 0 ]]; then
    echo "ngrok is not found, installing..."
    wget -q -nc https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
    tar -xzf ngrok-v3-stable-linux-amd64.tgz
    echo "Done!"
fi
