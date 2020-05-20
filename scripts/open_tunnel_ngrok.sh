#!/usr/bin/env bash

cmd="./ngrok start --all --config ngrok.conf"

kill -9 $(ps aux | grep $cmd | awk '{print $2}') 2> /dev/null

echo Opening tunnel
$cmd

