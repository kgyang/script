#!/usr/bin/env python

import os
import sys
import telnetlib

TIMEOUT = 10
def usage():
    cmd = os.path.basename(sys.argv[0])
    print('Usage:')
    print cmd + " <NE> <PORT> <USER> <PASSWORD>"
    sys.exit(1)

def login_ne(ne, port, user, password):
    tn = telnetlib.Telnet(ne, port)
    if not tn:
        print 'failed to connect ' + ne
        sys.exit(1)
    #tn.set_debuglevel(1)
    try:
        if not tn.read_until("login: ", TIMEOUT):
            raise NameError('username timeout')
        tn.write(user + "\n")
        if not tn.read_until("Password: ", TIMEOUT):
            raise NameError('password timeout')
        tn.write(password + "\n")
        if not tn.read_until("# ", TIMEOUT):
            raise NameError('password timeout')
    except (EOFError, NameError), detail:
        print "failed to login " + ne + ": " + detail
        tn.close()
        sys.exit(1)
    print '\nlogin ' + ne + ' successfully'

    # close echo
    tn.write("stty -echo\n")
    tn.read_until("# ")

    return tn

def logout_ne(tn):
    tn.close()

def run_script_on_ne_shell(tn, script):
    print '\nstarting to run'

    # send script to ne
    for ln in script.splitlines():
        tn.write(ln.lstrip()+'\n') # remove leading space to avoid some shell limitation
    # wait for response
    while True:
        res = tn.read_some()
        if not res: break
        sys.stdout.write(res)

if __name__ == "__main__":
    if len(sys.argv) != 5: usage()

    ne = sys.argv[1]
    neport = sys.argv[2]
    neuser = sys.argv[3]
    nepassword = sys.argv[4]

    tn = login_ne(ne, neport, neuser, nepassword)

    script = """
    {
    echo
    ls /
    exit
    }
    """

    run_script_on_ne_shell(tn, script)

    logout_ne(tn)

