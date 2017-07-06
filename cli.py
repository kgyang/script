#!/bin/env python

import sys
import telnetlib

__all__ = ["Cli"]

class Cli:
    explist = [(r'login: ', 'cli'),\
               (r'Username: ', 'admin'),\
               (r'Password: ', 'admin'),\
               (r'Do you acknowledge\? \(Y/N\)\?', 'y'),\
               (r'# ', '')]

    def __init__(self, host, port=23, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.tn = None
        self.prompt = r'# '
        self.login()

    def __del__(self):
        self.logout()

    def verbose(self, verb):
        if self.verbose != verb:
            if self.tn:
                if verb: self.tn.set_debuglevel(1)
                else: self.tn.set_debuglevel(0)
            self.verbose = verb

    def login(self):
        if self.tn: return
        self.tn = telnetlib.Telnet(self.host, self.port)
        if not self.tn:
            print 'connect fail'
            return
        if self.verbose: self.tn.set_debuglevel(1)
        complete = False
        for exp in self.explist:
            try:
                result = self.tn.expect([exp[0]], 30)
                if result[0] == -1:
                    print 'expect', exp[0], 'timeout'
                    break
                if exp[1]: self.tn.write(exp[1] + '\n')
            except EOFError, detail:
                self.close()
                print exp[0], exp[1], ":", detail
                break
            else:
                complete = (exp == self.explist[-1])
        if not complete:
            self.close()
            print 'login fail'
        else:
            self.getprompt()

    def logout(self):
        if self.tn:
            self.tn.write("logout\n")
            self.tn.expect(['Logging out....'], 5)
        self.close()

    def close(self):
        if self.tn:
            self.tn.close()
        self.tn = None

    def connected(self):
        return self.tn != None

    def getprompt(self):
        import re
        exp = re.compile(r'# .*# ', re.DOTALL)
        ok, output = self.runone('prompt', [exp])
        if ok and output[1:]:
            self.prompt = output[1]

    def runone(self, cmd, exp=[]):
        if not self.connected(): return (False, None)
        cmd = ' '.join(cmd.split()) # remove abundant space/tab
        if not exp: exp = [self.prompt]
        try:
            self.tn.write(cmd + '\n')
            result = self.tn.expect(exp, 60)
            if result[0] == -1:
                self.close()
            else:
                # remove the headline(which is cmd), tailline(which is prompt) 
                # and the empty lines
                return (True, filter(lambda x: x, result[2].splitlines()[1:-1]))
        except EOFError, detail:
            print 'running', cmd, "fail :", detail
            self.close()
        return (False, None)

    def runmultiple(self, cmds):
        text = list()
        if isinstance(cmds, str):
            cmds = cmds.splitlines()
        for cmd in cmds: 
            cmd = ' '.join(cmd.split()) # remove abundant space/tab
            if not cmd: continue
            print cmd
            result = self.runone(cmd)
            print result
            if not result[0]: return (False, text)
            text.append((cmd, result[1]))
        return (True, text)

    def runfile(self, file):
        try:
            f = open(file, 'r')
            cmds = f.read()
            f.close()
            return self.runmultiple(cmds)
        except IOError, detail:
            print detail
        return (False, None)

def test():
    import getopt
    ok = True
    help = False
    verbose = False
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v')
    except getopt.error:
        ok = False
    if not ok or len(args) != 1:
        help = True
    for o, a in optlist:
        if o == '-v': verbose = True
    if help:
        print 'Usage:', sys.argv[0], '[[-v] address]'
        print ' -v: enable verbose'
        sys.exit(1)
    if args:
        host = args[0]
        cli = Cli(host, 23, verbose)
        #print cli.runone('show general name')
        print cli.runmultiple('''
            show general name
            show general date
            show version''')
        #print cli.runfile('/home/kgyang/oamcli')

def cportstr(shelf, slot, port):
    return str(shelf) + '/' + str(slot) + '/c' + str(port)

def lportstr(shelf, slot, port):
    return str(shelf) + '/' + str(slot) + '/l' + str(port)

def test2():
    shelf = 2
    slot = 3
    cportnum = 1 
    lportnum = 2
    cmdlist = list()
    # card
    cmdlist.append('config slot ' + str(shelf) + '/' + str(slot) + ' type 11dpe12')
    cmdlist.append('config card ' + str(shelf) + '/' + str(slot) + ' mode qinq')
    # port type
    for i in range(1,cportnum + 1):
        cport = cportstr(shelf, slot, i)
        cmdlist.append('config interface ' + cport + ' type 1GbE')
    for i in range(1,lportnum + 1):
        lport = lportstr(shelf, slot, i)
        cmdlist.append('config interface ' + lport + ' type otu2')
    # vts and vts xc and esncp
    for i in range(1,cportnum + 1):
        cport = cportstr(shelf, slot, i)
        cvts = cport + '/1'
        # cvts
        cmdlist.append('config interface ' + cport + ' vts1 egress cevlanid all')
        cmdlist.append('config interface ' + cport + ' vts1 ingress cevlanid all')
        for j in range(1,lportnum + 1):
            lport = lportstr(shelf, slot, j)
            # lvts
            cmdlist.append('config interface ' + lport + ' vts' + str(i) + ' egress svlanid ' + str(i))
            cmdlist.append('config interface ' + lport + ' vts' + str(i) + ' ingress svlanid ' + str(i))
        l1vts = lportstr(shelf, slot, 1) + '/' + str(i)
        l2vts = lportstr(shelf, slot, 2) + '/' + str(i)
        # vts xc
        cmdlist.append('config vtsxc ' + cvts + ' ' + l1vts + ' create ' + \
                       cvts + '-' + l1vts + ' profile cir 100 pir 100')
        cmdlist.append('config vtsxc ' + cvts + ' ' + l1vts + ' state up')
        cmdlist.append('config vtsxc ' + l1vts + ' ' + cvts + ' create ' + \
                       l1vts + '-' + cvts + ' profile cir 100 pir 100')
        cmdlist.append('config vtsxc ' + l1vts + ' ' + cvts + ' state up')
        # esncp
        cmdlist.append('config aps group ' + str(i) + ' create ' + cvts + ' ' + l2vts + ' ' + l1vts + ' uni')
    rc, results = Cli('127.0.0.1').runmultiple(cmdlist)

def test3():
    shelf = 1
    slot = 8
    cportnum = 1
    lportnum = 2
    cmdlist = list()
    for i in range(1,cportnum + 1):
        cport = cportstr(shelf, slot, i)
        cvts = cport + '/1'
        l1vts = lportstr(shelf, slot, 1) + '/' + str(i)
        # esncp
        cmdlist.append('config aps group ' + str(i) + ' delete yes')
        # vts xc
        cmdlist.append('config vtsxc ' + cvts + ' ' + l1vts + ' state down')
        cmdlist.append('config vtsxc ' + cvts + ' ' + l1vts + ' delete')
        cmdlist.append('config vtsxc ' + l1vts + ' ' + cvts + ' state down')
        cmdlist.append('config vtsxc ' + l1vts + ' ' + cvts + ' delete')
        # cvts
        cmdlist.append('config interface ' + cport + ' vts1 egress cevlanid none')
        cmdlist.append('config interface ' + cport + ' vts1 ingress cevlanid none')
        for j in range(1,lportnum + 1):
            lport = lportstr(shelf, slot, j)
            # lvts
            cmdlist.append('config interface ' + lport + ' vts' + str(i) + ' egress svlanid none')
            cmdlist.append('config interface ' + lport + ' vts' + str(i) + ' ingress svlanid none')
    ret, results = Cli('127.0.0.1').runmultiple(cmdlist)

if __name__ == '__main__':
    test2()

