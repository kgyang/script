#!/bin/sh
# We have 1gbit upload and want to guarantee each user a certain amount of it.
# If one user does not use its full quota, the unused quota get evenly distributed amongst the other users.
 
# Variables
#IF=br-lan
#TC=$(which tc)
#IPT=$(which iptables)
#IPTMOD="iptables -t mangle -A POSTROUTING -o $IF"
IPAD=192.168.1.125
IPAD_MAC=4A:B9:2F:3E:23:E8
REDMI_MAC=28:16:7F:2F:77:C2
REDMI=192.168.1.109
 
#insmod sch_htb
 
/sbin/tc qdisc del dev br-lan root 2>/dev/null
/usr/sbin/iptables -t mangle -F
/usr/sbin/iptables -t mangle -X

/sbin/tc qdisc add dev br-lan root handle 1: htb default 30
/sbin/tc class add dev br-lan parent 1:  classid 1:1  htb rate 1gbit
/sbin/tc class add dev br-lan parent 1:1 classid 1:10 htb rate 30kbit
/sbin/tc class add dev br-lan parent 1:1 classid 1:20 htb rate 30kbit
 
/usr/sbin/iptables -t mangle -A POSTROUTING -o br-lan -d $IPAD -j CLASSIFY --set-class 1:10
/usr/sbin/iptables -t mangle -A POSTROUTING -o br-lan -d $REDMI -j CLASSIFY --set-class 1:20
#/usr/sbin/iptables -t mangle -A POSTROUTING -o br-lan -m mac --mac-destination $IPAD_MAC -j CLASSIFY --set-class 1:10
#/usr/sbin/iptables -t mangle -A POSTROUTING -o br-lan -m mac --mac-destination $REDMI_MAC -j CLASSIFY --set-class 1:20
