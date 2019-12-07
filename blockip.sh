#!/bin/bash

BLOCKIP_CHAIN=blockip
IP_DENY_FILE=$HOME/script/ips_deny.txt

bad_ip_in_log()
{
    {
    for f in /var/log/auth.log /var/log/secure
    do
        [[ -f $f ]] && cat $f
    done

    for f in /var/log/auth*.gz /var/log/secure*.gz
    do
        [[ -f $f ]] && zcat $f
    done
    } |
    sed -n 's/.*Failed password for .* from \(.*\) port.*/\1/p' |
    awk '{num[$1]++;}END{for (ip in num) if (num[ip] >= 10) print(ip)}'
}

bad_ip_in_file()
{
    [[ -f $IP_DENY_FILE ]] && grep -v '#' $IP_DENY_FILE
}

bad_ip()
{
    { bad_ip_in_log; bad_ip_in_file; } | sort | uniq
}

start()
{
    ips=$(bad_ip)
    [[ -n "$ips" ]] || return

    stop

    iptables -N $BLOCKIP_CHAIN
    iptables -I INPUT 1 -j $BLOCKIP_CHAIN

    for ip in $ips
    do
        iptables -A $BLOCKIP_CHAIN -s $ip -j DROP
    done
}

stop()
{
    iptables -nL $BLOCKIP_CHAIN 2&>/dev/null || return
    iptables -D INPUT -j $BLOCKIP_CHAIN
    iptables -F $BLOCKIP_CHAIN
    iptables -X $BLOCKIP_CHAIN
}

if [[ "$1" == "start" ]]
then
    start
elif [[ "$1" == "stop" ]]
then
    stop
else
    echo "$0 <start|stop>" >&2
fi
