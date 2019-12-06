#!/bin/bash

# scan auth and secure log to find out attacking IPs (failure times >= 10) then block them using iptables.

BLOCKIP_CHAIN=blockip

dump_log()
{
    for f in /var/log/auth.log /var/log/secure
    do
        [[ -f $f ]] && cat $f
    done

    for f in /var/log/auth*.gz /var/log/secure*.gz
    do
        [[ -f $f ]] && zcat $f
    done
}

start()
{
    ips=$(dump_log | sed -n 's/.*Failed password for .* from \(.*\) port.*/\1/p' |
          awk '{num[$1]++;}END{for (ip in num) if (num[ip] >= 10) print(ip)}')
    [[ -n "$ips" ]] || {
        echo "no suspicious ip"
        return
    }

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
