#!/usr/bin/env python
import sys
from atelnet import ATelnet

__all__ = ["ITelnet"]

class ITelnet(ATelnet):
    def __init__(self, ip, innetc, innetd, user='', password='', prompt='# ', verbose=False):
        self.ip = ip
        self.innetc = innetc
        self.innetd = innetd
        self.port_forwarding = 20000 + innetc*100 + innetd
        self.verbose = verbose
        self.setupforward()
        super(ITelnet, self).__init__(ne, user=user, password=password,\
              port=self.port_forwarding, prompt=prompt, verbose=verbose)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()
        self.clearforward()
        super(ITelnet, self).__exit__(exc_type, exc_value, traceback)

    def clearforward(self):
        self.configforwardrules('-D')

    def setupforward(self):
        self.configforwardrules('-A')

    def configforwardrules(self, action):
        '''
           iptables -t nat -A PREROUTING -i oamp -p tcp --dport 20119 -j DNAT --to 192.168.1.19:23
           iptables -A FORWARD -p tcp -d 192.168.1.19 --dport 23 -j ACCEPT
           iptables -t nat -A POSTROUTING -p tcp -d 192.168.1.19 --dport 23 -o ilan -j MASQUERADE
        '''
        tn = ATelnet(self.ip, verbose=self.verbose)
        if not tn: return
        if not tn.connected(): return
        lc_ip = '192.168.' + str(self.innetc) + '.' + str(self.innetd)
        preroute = 'iptables -t nat ' + action + ' PREROUTING -i oamp -p tcp --dport ' + str(self.port_forwarding) + \
                   ' -j DNAT --to ' + lc_ip + ':23'
        forward = 'iptables ' + action + ' FORWARD -p tcp -d ' + lc_ip + ' --dport 23 -j ACCEPT'
        postroute = 'iptables -t nat ' + action + ' POSTROUTING -p tcp -d ' + lc_ip + ' --dport 23 -o ilan -j MASQUERADE'
        tn.run(preroute)
        tn.run(forward)
        tn.run(postroute)

def parse_args():
    import os
    import getopt
    ok = True
    dohelp = False
    verbose = False
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v')
    except getopt.error:
        ok = False
    if not ok or len(args) < 3:
        dohelp = True
    if dohelp: usage()

    for o, a in optlist:
        if o == '-v': verbose = True

    ip = args[0]
    innetc = int(args[1])
    innetd = int(args[2])
    user = 'root'
    password = ''
    if len(args) > 3: user = args[3]
    if len(args) > 4: password = args[4]

    return (ne, innetc, innetd, user, password, verbose)

def usage():
    print(r"""Telnet client class for innet.
Usage: itelnet.py [-v] <IP> <INNETC> <INNETD> [<LOGIN> <PASSWORD>]
       -v: enable verbose

Example 1):
>>> from itelnet import ITelnet
>>> lc = ITelnet('1.2.3.4', 1, 19)
>>> rc, res = lc.run('ls /')
>>> if rc:
>>>    for ln in res: print(ln)

Example 2):
-> { echo 'ls /'; echo 'ls /tmp'; } | ./itelnet.py 1.2.3.4 1 19

Example 3):
-> ./itelnet.py 1.2.3.4 1 19
-> ./itelnet.py 1.2.3.4 1 2 username password

""")
    sys.exit(1)



if __name__ == '__main__':
    ip, innetc, innetd, user, password, verbose = parse_args()
    with ITelnet(ip, innetc, innetd, user=user, password=password, verbose=verbose) as tn:
        if tn.is_script_mode():
            tn.runloop()
        else:
            tn.interact()
