#!/bin/sh
 
iptables -t mangle -F
iptables -t mangle -X
tc qdisc del dev br-lan root
