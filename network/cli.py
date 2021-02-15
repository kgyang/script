#!/usr/bin/env python

import sys
import re
import telnetlib
import threading

__all__ = ["Cli"]

LOGIN_SUCCESS = 0
CONNECT_FAIL = 1
LOGIN_FAIL = 2
MAX_ANTI_IDLE_TIME = 60
MAX_WAIT_TIME = 5

class Cli(object):
    def __init__(self, ne, port=23, user='user', password='password', verbose=False, logintimeout=5):
        self.ne = ne
        self.port = port
        self.user = user
        self.password = password
        self.verbose = verbose
        self.logintimeout = logintimeout

        self.wlock = threading.Lock()
        self.timer = None
        self.listener = None

        self.tn = None
        self.prompt = r'# '
        self.paging_enabled = True
        self.echo_enabled= True

        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def verbose(self, verb):
        if self.verbose != verb:
            if self.tn:
                if verb: self.tn.set_debuglevel(1)
                else: self.tn.set_debuglevel(0)
            self.verbose = verb

    def login(self):
        self.loginStyle = [(r'Username: ', self.user),\
                           (r'Password: ', self.password),\
                           (r'# ', '')]
        if self.tn: return LOGIN_SUCCESS
        try:
            self.tn = telnetlib.Telnet(self.ne, self.port, self.logintimeout)
        except:
            sys.stderr.write(self.ne + ': failed to connect\n')
            self.tn = None
            return CONNECT_FAIL

        if self.verbose: self.tn.set_debuglevel(1)

        complete = False
        for style in loginStyle: 
            try:
                exp = style[0]
                resp = style[1]
                res = self.tn.expect([exp.encode('ascii')], self.logintimeout)
                if res[0] == -1:
                    sys.stderr.write(self.ne + ': expect ' + exp + ' timeout\n')
                    break
                else:
                    if resp:
                        self.write(resp + '\n')
                    else:
                        complete = True
                        # get prompt from tail line
                        self.prompt = res[2].splitlines()[-1].decode('ascii')
            except EOFError as err:
                self.close()
                sys.stderr.write(self.ne + ': ' + exp + ' ' + resp + ': ' + str(err) + '\n')
                break

        if not complete:
            self.close()
            return LOGIN_FAIL
        else:
            return LOGIN_SUCCESS

    def logout(self):
        if self.connected():
            self.write(b"logout\n")
            #self.tn.expect([b'Logging out....'], 2)
        self.close()

    def close(self):
        if self.tn:
            self.tn.close()
        self.tn = None
        self.prompt = r'# '
        self.paging_enabled = True
        self.echo_enabled = True

    def connected(self):
        return (self.tn and not self.tn.eof)

    def write(self, cmd):
        """Send <cmd> to remote server.

        This function is thread-safe. If connection closed, close() will be called.

        """
        if self.tn:
            try:
                self.wlock.acquire()
                if not isinstance(cmd, bytes): cmd = cmd.encode('ascii')
                self.tn.write(cmd)
            except OSError:
                self.close()
            finally:
                self.wlock.release()

    def set_paging_status(self, enabled):
        if self.paging_enabled == enabled:
            return

        if enabled:
            cmd = 'paging status enabled'
        else:
            cmd = 'paging status disabled'
        self.write(cmd + '\n')
        if self.connected():
            res = self.tn.expect([b'# '], self.logintimeout)
            if res[0] == 0:
                self.paging_enabled = enabled

    def set_echo_status(self, enabled):
        if self.echo_enabled == enabled:
            return

        self.write('echo\n')
        if self.connected():
            res = self.tn.expect([b'# '], self.logintimeout)
            if res[0] == 0:
                self.echo_enabled = enabled

    def run(self, cmd, exp='', timeout=60):
        """Send <cmd> to remote server and read response until one of <exp> list
        received or <timeout=60> seconds timeout.

        If no exp specified, wait for prompt. The prompt is updated each time
        after response received.

        Return a tuple of two items: success flag of execution; and the list of
        response. Note the response list does not include <exp>.

        This function will disable echo and paging firstly.
        'prompt', 'paging', 'echo' commands are not allowed to be run.

        """
        if not self.connected(): return (False, list())

        clist = cmd.split()

        # disable paing and echo would simplify parsing
        self.set_paging_status(False)
        self.set_echo_status(False)

        # do not allow paging and echo  and prompt command
        if clist[0] == 'paging' or clist[0] == 'echo' or clist[0] == 'prompt':
            return (True, list())


        if not exp:
            # prompt will be inserted by middle commands, so replace with '.*'
            exp = [(self.prompt[:-2] + '.*# ').encode('ascii')]

        if not isinstance(exp, list):
            exp = [exp]

        # capture this if paging status is enabled by user command unexpectedly
        exp.append(br'more\? y=\[yes\] q=\[quit\].*')

        try:
            self.write(cmd + '\n')
            res = list()
            while True:
                resp = self.tn.expect(exp, timeout)
                if resp[0] == -1:
                    sys.stderr.write(self.ne + ": " + cmd + " no resp\n")
                    return (False, list())
                elif resp[0] == (len(exp) - 1): # paging
                    # remove the the tailline(which is paging indication) 
                    res += resp[2].decode('ascii').splitlines()[:-1]
                    self.write(b'y')
                else:
                    res += resp[2].decode('ascii').splitlines()
                    break
        except:
            sys.stderr.write(self.ne + ": " + cmd + " FAIL\n")
            self.close()
            return (False, list())

        # remove tailline(which is prompt)
        return (True, list(filter(None, res[:-1])))


    def runloop(self, prompt=''):
        """Repeatedly forward input from stdin to remote server for execution and
        print response until EOF received from stdin or connection closed.

        Normally this function is called to receives input from pipeline. 

        The run loop ends in one of following conditions:
        1) connection closed
        2) EOF received from stdin

        """
        if not self.connected(): return

        try:
            self.start_anti_idle_timer()

            use_rawinput = True
            try:
                import readline
            except ImportError:
                use_rawinput = False

            while True:
                if use_rawinput:
                    try:
                        ln = raw_input(prompt)
                    except EOFError:
                        break
                else:
                    if prompt:
                        sys.stdout.write(prompt)
                        sys.stdout.flush()
                    ln = sys.stdin.readline()
                    if not len(ln):
                        break

                ln = ln.rstrip('\r\n')
                if not ln:
                    continue
                rc, res = self.run(ln)
                if not rc or not self.connected():
                    break
                for l in res:
                    sys.stdout.write(l + '\n')
        finally:
            self.cancel_anti_idle_timer()

    def interact(self):
        """Interaction function, emulates a cli client.


        Features:
        1) each single key pressed is sent to remote server
        2) how to exit: press logout command or any commands cause connection closed
        3) anti idle thread is created to send NOP every 1 minutes to prevent 
           connection from being closed by remote server when there's no user input
           for long time. The thread terminates when connection closed
        4) listener thread is created to print server response. The thread
           terminates when connection closed.

        Note:
        If run() was called before, echo is disabled. set_echo_status(True) shall
        be called to enable echo before calling interact().

        """
        if not self.connected(): return

        try:
            if sys.platform == 'win32':
                import msvcrt
            else:
                import tty, termios
                fd = sys.stdin.fileno()
                old_settings = termios.tcgetattr(fd)
                tty.setraw(fd)

            self.start_listener()
            self.start_anti_idle_timer()

            sys.stdout.write(self.prompt)

            pre_ch = b''
            while True:
                if sys.platform == 'win32':
                    ch = msvcrt.getch()
                    if ch == b'\xe0':
                        ch = b'\x1b'
                    if pre_ch == b'\x1b':
                        if ch == b'K': ch = b'[D' # left arrow
                        elif ch == b'M': ch = b'[C' # right arrow
                        elif ch == b'H': ch = b'[A' # up arrow
                        elif ch == b'P': ch = b'[B' # down arrow
                else:
                    ch = sys.stdin.read(1)
                if not ch:
                    break
                if not self.connected():
                    break

                self.write(ch)
                pre_ch = ch

                if not self.connected():
                    break
        finally:
            if sys.platform != 'win32':
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
            self.cancel_anti_idle_timer()

    def start_listener(self):
        """Start a thread to run socket listener."""
        if not self.listener:
            #self.listener = threading.Thread(target=self.tn.listener)
            self.listener = threading.Thread(target=self.listener_handler)
            self.listener.start()

    def listener_handler(self):
        # we do not use the listener in telnetlib.py. The reason is that
        # listener use read_eager which cost CPU too much. So we define
        # the listener_handler as a new listener whchi use read_some()
        # to block when no data available
        # set socket to block to avoid timeout exception
        self.tn.sock.setblocking(True)
        while self.connected():
            try:
                data = self.tn.read_some()
            except EOFError:
                print('*** Connection closed by remote host ***')
                return
            if data:
                sys.stdout.write(data.decode('ascii'))
                sys.stdout.flush()
            else:
                break

    def start_anti_idle_timer(self):
        """Start a thread to run anti idle timer."""
        self.timer = threading.Timer(MAX_ANTI_IDLE_TIME, self.anti_idle_timer_handler)
        self.timer.start()

    def cancel_anti_idle_timer(self):
        if self.timer:
            self.timer.cancel()
            self.timer = None

    def anti_idle_timer_handler(self):
        """If connected, send NOP and restart anti idle timer."""
        if not self.connected(): return
        self.send_nop()
        self.start_anti_idle_timer()

    def send_nop(self):
        """Send NOP to remote server to anti idle."""
        if not self.connected(): return
        try:
            self.wlock.acquire()
            nop = telnetlib.IAC + telnetlib.NOP
            if self.verbose:
                self.tn.msg("send %r", nop)
            self.tn.sock.sendall(nop) # write() doubles IAC, so use sendall
        finally:
            self.wlock.release()

    def is_script_mode(self):
        if sys.platform != 'win32':
            try:
                import termios
                termios.tcgetattr(sys.stdin.fileno())
            except termios.error:
                return True
        return False

def test():
    print(Cli('127.0.0.1').run('help'))

def usage():
    print(r"""CLI client class.
Usage: cli.py [-v] <MACHINE>
    -v: enable verbose'
Example 1):
>>> from cli import Cli
>>> with Cli('1.2.3.4') as cli:
>>>     rc, res = cli.run('help')
>>>     if rc:
>>>         for ln in res: print(ln)

Example 2):
-> { echo 'help'; } | ./cli.py 1.2.3.4

Example 3):
-> ./cli.py 1.2.3.4

""")
    sys.exit(1)

if __name__ == '__main__':
    import getopt
    ok = True
    do_help = False
    verbose = False
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v')
    except getopt.error:
        ok = False
    if not ok or len(args) != 1:
        do_help = True
    if do_help: usage()
    for o, a in optlist:
        if o == '-v': verbose = True


    ne = args[0]
    with Cli(ne, 23, verbose=verbose) as cli:
        if not cli.connected(): sys.exit(1)
        if cli.is_script_mode():
            cli.runloop()
        else:
            cli.interact()
