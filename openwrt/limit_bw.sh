#!/bin/sh
# We have 1gbit upload and want to guarantee each user a certain amount of it.
# If one user does not use its full quota, the unused quota get evenly distributed amongst the other users.
 
# Variables
IF=br-lan
#TC=$(which tc)
#IPT=$(which iptables)
IPTMOD="iptables -t mangle -A POSTROUTING -o $IF"
IPAD=192.168.1.125
 
#insmod sch_htb
 
tc qdisc del dev br-lan root
iptables -t mangle -F
iptables -t mangle -X

tc qdisc add dev br-lan root handle 1: htb default 30
tc class add dev br-lan parent 1:  classid 1:1  htb rate 1gbit
tc class add dev br-lan parent 1:1 classid 1:10 htb rate 10kbit
 
iptables -t mangle -A POSTROUTING -o br-lan -d $IPAD -j CLASSIFY --set-class 1:10
