#!/bin/sh
 
/usr/sbin/iptables -t mangle -F
/usr/sbin/iptables -t mangle -X
/sbin/tc qdisc del dev br-lan root
