#!/usr/bin/env bash

kill -9 $(ps aux | grep 'ngrok' | awk '{print $2}') 2> /dev/null

echo Opening tunnel
./ngrok start --all --config ngrok.conf
