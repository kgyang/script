#!/bin/env python

import sys
import telnetlib

__all__ = ["Cli"]

CLI_LOGIN='xxxxx'
CLI_LOGIN_PASSWORD='yyyyy'
class Cli:
    oldLoginStyle = [(r'login: ', 'cli'),\
                     (r'Password: ', 'cli'),\
                     (r'Username: ', CLI_LOGIN),\
                     (r'Password: ', CLI_LOGIN_PASSWORD),\
                     (r'Do you acknowledge\? \(Y/N\)\?', 'y'),\
                     (r'# ', '', True)]
    loginStyle = [(r'login: ', 'cli'),\
                  (r'Username: ', CLI_LOGIN),\
                  (r'Password: ', CLI_LOGIN_PASSWORD),\
                  (r'Do you acknowledge\? \(Y/N\)\?', 'y'),\
                  (r'# ', '')]

    def __init__(self, host, port=23, verbose=False):
        self.host = host
        self.port = port
        self.verbose = verbose
        self.tn = None
        self.prompt = r'# '
        if not self.login(self.loginStyle):
            print 'NE runs old software, retry login with old style'
            self.login(self.oldLoginStyle)

    def __del__(self):
        self.logout()

    def verbose(self, verb):
        if self.verbose != verb:
            if self.tn:
                if verb: self.tn.set_debuglevel(1)
                else: self.tn.set_debuglevel(0)
            self.verbose = verb

    def login(self, loginStyle):
        if self.tn: return
        self.tn = telnetlib.Telnet(self.host, self.port)
        if not self.tn:
            print 'connect fail'
            return False
        if self.verbose: self.tn.set_debuglevel(1)
        complete = False
        for style in loginStyle: 
            try:
                exp = style[0]
                resp = style[1]
                result = self.tn.expect([exp], 5)
                if result[0] == -1:
                    print 'expect', exp, 'timeout'
                    break
                else:
                    if resp: self.tn.write(resp + '\n')
            except EOFError, detail:
                self.close()
                print exp, resp, ":", detail
                break
            else:
                complete = (style == loginStyle[-1])
        if not complete:
            self.close()
            return False
        else:
            self.getprompt()
            return True

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
        exp.append(r'more\? y=\[yes\] q=\[quit\].*')
        try:
            self.tn.write(cmd + '\n')
            result = list()
            while True:
                resp = self.tn.expect(exp, 60)
                if resp[0] == -1:
                    self.close()
                    return (False, None)
                elif resp[0] == (len(exp) - 1): # paging
                    # remove the the tailline(which is paging indication) 
                    result += resp[2].splitlines()[:-1]
                    self.tn.write('y')
                else:
                    result += resp[2].splitlines()
                    break
        except EOFError, detail:
            print 'running', cmd, "fail :", detail
            self.close()
            return (False, None)
        # remove the headline(which is cmd), tailline(which is prompt) and empty lines  
        return (True, filter(lambda x: x, result[1:-1]))

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
            show general date
            show version''')

if __name__ == '__main__':
    test()

