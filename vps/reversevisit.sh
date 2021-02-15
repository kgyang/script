#!/bin/bash

[[ "$1" == "-h" ]] && exit

SERVER_IP=45.78.43.92
SERVER_PORT=29631
SERVER_LISTEN_PORT=xxx
SERVER_USER=xxx
set -x
while true
do
	echo "$(date): establish reverse bind connection to $SERVER_IP"
	ssh -p $SERVER_PORT -R $SERVER_LISTEN_PORT:localhost:22 $SERVER_USER@$SERVER_IP
done
