#!/usr/bin/env bash

remote_port_in=5557
remote_port_out=5558
port_in=5557
port_out=5558

KEY=$1
REMOTE_HOST=$2

if [[ -z $KEY ]] || [[ -z $REMOTE_HOST ]]; then
	echo Usage: open_tunnel_ssh.sh path_to_key.pem remote_host
	exit
fi

port_out=5558

chmod 400 $KEY

cmd_in="ssh -f -N -T -R $remote_port_in:localhost:$port_in -i $KEY -o StrictHostKeyChecking=no $REMOTE_HOST"
cmd_out="ssh -f -N -T -R $remote_port_out:localhost:$port_out -i $KEY -o StrictHostKeyChecking=no $REMOTE_HOST"

kill -9 $(ps aux | grep "$cmd_in" | awk '{print $2}') 2> /dev/null
kill -9 $(ps aux | grep "$cmd_out" | awk '{print $2}') 2> /dev/null

echo Open tunnels
set +x
$cmd_in
$cmd_out

