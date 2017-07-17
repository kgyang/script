#!/bin/ksh

#this script download files from ftp server

usage()
{
	echo "$(basename ${0}) <filename>..." >&2
	exit 1 
}

fail()
{
	echo "$*" >&2
	exit 1
}

[[ $# -gt 0 ]] || usage
[[ -n "$PC_FTP_LOGNAME" ]] || fail 'please export PC_FTP_LOGNAME'
[[ -n "$PC_FTP_PASSWORD" ]] || fail 'please export PC_FTP_PASSWORD'

FTP_SERVER=''
FTP_LOGNAME=$PC_FTP_LOGNAME
FTP_PASSWD=$PC_FTP_PASSWORD

[[ -n $FTP_SERVER ]] || {
	# SSH_CLIENT=::ffff:10.0.0.18 56287 22
	# REMOTEHOST=10.0.0.18
	if [[ -n $REMOTEHOST ]]; then
		FTP_SERVER=$REMOTEHOST
	elif [[ -n $SSH_CLIENT ]]; then
		FTP_SERVER=$(echo ${SSH_CLIENT} | \
		sed -e "s/[^[:digit:]]*\([[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*\.[[:digit:]]*\).*/\1/")
	fi
}
[[ -n $FTP_SERVER ]] || fail "unknown server, exit"

echo "check connection..."
ping -c 1 -W 2 $FTP_SERVER >> /dev/null || {
	echo "connection blocked, use CSL account to do authentication..."
	ftp $FTP_SERVER
}
echo "check connection after authentication..."
ping -c 1 -W 2 $FTP_SERVER >> /dev/null || fail "connection still blocked"


echo "connecting ftp server $FTP_SERVER ..."
echo ""

ftp -n $FTP_SERVER << SCRIPT
user $FTP_LOGNAME $FTP_PASSWD
binary
verbose

$(
for file in $@ ;do
	echo "lcd $(dirname $file)"
	echo "get $(basename $file)"
done
)

quit

SCRIPT

exit 0
