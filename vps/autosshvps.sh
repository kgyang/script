#!/bin/bash

[[ "$1" == "-h" ]] && exit

SERVER_IP=45.78.43.92
SERVER_PORT=29631
SERVER_USER=kgyang

[[ -f ~/.ssh/id_rsa && -f ~/.ssh/id_rsa.pub ]] || {
	ssh-keygen || { echo "key gen fail" >&2; exit 1; }
}

set -x

ssh -p $SERVER_PORT $SERVER_USER@$SERVER_IP 'mkdir -p .ssh' || {
	echo "connect $SERVER_IP fail" >&2
	exit 1
}

scp -P $SERVER_PORT ~/.ssh/id_rsa.pub $SERVER_USER@$SERVER_IP:.ssh/authorized_keys || {
	echo "copy pub key to $SERVER_IP fail" >&2
	exit 1
}
