#!/usr/bin/env python

import os
import stat
import sys
import re
import telnetlib
import threading

__all__ = ["ATelnet"]

MAX_ANTI_IDLE_TIME = 60

class ATelnet(object):
    def __init__(self, ip, port=23, user='user', password='password', prompt='# ', logintimeout=5, verbose=False):
        self.ip = ip
        self.port = port
        self.user = user
        self.password = password
        self.default_prompt = prompt
        self.logintimeout = logintimeout
        self.verbose = verbose

        self.wlock = threading.Lock()
        self.timer = None
        self.listener = None

        self.tn = None
        self.prompt = self.default_prompt
        self.echo_enabled = True

        self.login()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.logout()

    def login(self):
        try:
            self.tn = telnetlib.Telnet(self.ip, self.port, self.logintimeout)
            if self.verbose: self.tn.set_debuglevel(1)
            if not self.tn.expect([b"login: "], self.logintimeout)[1]:
                raise NameError('waiting for login timeout')
            if self.password:
                if not self._run(self.user, "Password: ", timeout=self.logintimeout):
                    raise NameError('waiting for password timeout')
                if not self._run(self.password, timeout=self.logintimeout):
                    raise NameError('password invalid')
            else:
                if not self._run(self.user, timeout=self.logintimeout):
                    raise NameError('user invalid')

            if self.verbose:
                print('\nlogin ' + self.ip + ":" + str(self.port) + ' successfully')

        except (EOFError, NameError) as err:
            print("failed to login " + self.ip + "(" + str(self.port) + "): " + str(err))
            self.logout()
            return False
        except:
            print("failed to login " + self.ip + "(" + str(self.port)  + "): " + str(sys.exc_info()[0]))
            self.logout()
            return False
        return True

    def logout(self):
        if self.connected():
            self.write('exit\n')
            self.tn.close()
        self.tn = None
        self.prompt = self.default_prompt
        self.echo_enabled = True

    def connected(self):
        return (self.tn and not self.tn.eof)

    def reconnect(self):
        self.logout()
        self.tn = self.login()

    def write(self, cmd):
        if self.tn:
            try:
                self.wlock.acquire()
                if not isinstance(cmd, bytes): cmd = cmd.encode('ascii')
                self.tn.write(cmd)
            except OSError:
                self.logout()
            finally:
                self.wlock.release()


    def run(self, cmd, exp='', timeout=60):
        """Send <cmd> to remote server and read response until <exp> received or
        <timeout=60> seconds timeout.

        If no exp specified, expect prompt. 

        Return a tuple of two items: success flag of execution; and the list of
        response. Note the response list does not include <exp>.

        This function will do following two things firstly to simplify parsing:
        1) disable echo, which could simplify parsing response
        2) set fixed and unusual prompt('root@# ') to avoid possible expect() failure
        'export PS1=xxx', 'stty echo' commands are not allowed to be run.

        """
        if not self.connected():
            return (False, list())

        self.set_echo_status(False)
        self.set_fixed_prompt()

        if cmd.find('stty echo') == 0 or cmd.find('export PS1=') == 0:
            return (True, list())

        ret = self._run(cmd, exp, timeout)
        if not ret:
            return (False, list())
        else:
            # some pack(PTPCTL) could not disable echo, so check head line
            # to remove echo line
            if ret[0] == cmd:
                ret = ret[1:]
            return (True, ret[:-1]) # remove expect in the tail

    def _run(self, cmd, exp='', timeout=60):
        """Internal function. Return list of response including <exp>
        """
        if not cmd: return list()
        if not exp: exp = self.prompt
        if not self.tn: return list()
        try:
            if cmd[-1] != '\n': cmd = cmd + '\n'
            self.write(cmd)
            res = self.tn.expect([exp.encode('ascii')], timeout=timeout)
        except:
            self.logout()
            return list()
        if not res[1]:
            self.logout()
            return list()
        return res[2].decode('ascii').splitlines()

    def set_echo_status(self, enabled):
        """Be careful 'stty -echo' in some pack will change prompt, so
        this function must be called before set_fixed_prompt.
        """
        if self.verbose: print('set echo status ' + str(enabled))
        if self.echo_enabled == enabled:
            return

        if enabled:
            ret = self._run('stty echo')
        else:
            ret = self._run('stty -echo')
        if ret:
            self.echo_enabled = enabled

    def set_fixed_prompt(self):
        """ Some machines' bash prompt is simple as '# ', it would cause
        command run fail if the command resp contains '# ', so
        we change to use complitated prompt to reduce possible expect failure.
        """
        if self.prompt == self.default_prompt:
            self.prompt = self.user + '@' + self.default_prompt
            ret = self._run("export PS1='" + self.prompt + "'")
            if not ret:
                self.prompt = self.default_prompt
            # some LC (PTPCTL i.e.) does not support echo, so do read to clean buf
            self.tn.read_very_eager()

    def runloop(self, prompt=''):
        """Repeatedly forward input from stdin to remote server for execution
        and print response until EOF received from stdin or connection closed.

        Normally this function is called to receives input from pipeline.

        The run loop ends in one of following conditions:
        1) connection closed
        2) EOF received from stdin
        2) exit command

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
                if not ln : continue

                if ln == 'exit':
                    break

                rc, res = self.run(ln)
                if not rc or not self.connected():# break due to connection closed
                    break

                for l in res:
                    sys.stdout.write(l + '\n')
        finally:
            self.cancel_anti_idle_timer()

    def interact(self):
        """Interaction funtion, emulates telnet client.

        Features:
        1) each single key pressed is sent to remote server
        2) how to exit: press Ctrl-D twice or any command cause connection closed
        3) anti idle thread is created to send NOP every 1 minutes to prevent
           connection from being closed by remote server when there's no user input
           for long time. The thread terminates when connection closed
        4) listener thread is created to print server response. The thread
           terminates when connection closed.

        Note:
        If run() was called before, echo is disabled. set_echo_status(True) shall
        be called to enable echo before calling interact().

        """
        #if self.tn: self.tn.interact()
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

            # press '\n' to display prompt
            self.write('\n')

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
                # enter 'ctrl-D' twice to exit
                if pre_ch == '\x04' and ch == '\x04':
                    break

                self.write(ch)
                pre_ch = ch

                if not self.connected():
                    break
        finally:
            if sys.platform != 'win32':
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

            self.cancel_anti_idle_timer()

            self.logout()

    def start_listener(self):
        """Start a thread to run socket listener."""
        if not self.listener:
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

    def sendfile(self, filename, to=''):
        ''' only applies to text file '''
        if not to: to = filename
        try:
            with open(filename, 'r') as f:
                text = re.sub("\t", "    ", f.read())
                sendcmd = "(cat <<'EOFXYZ'\n" + text + "\nEOFXYZ\n)> " + to
                if not self._run(sendcmd):
                    print('send file fail')
                    return False
                if (os.stat(filename).st_mode & stat.S_IXUSR):
                    self._run('chmod +x ' + to)
        except OSError:
            print('can not open file')
            return False
        return True

    def is_script_mode(self):
        if sys.platform != 'win32':
            try:
                import termios
                termios.tcgetattr(sys.stdin.fileno())
            except termios.error:
                return True
        return False

def parse_args():
    import getopt
    ok = True
    dohelp = False
    verbose = False
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'v')
    except getopt.error:
        ok = False
    if not ok or len(args) != 1:
        dohelp = True

    if dohelp: usage()

    for o, a in optlist:
        if o == '-v': verbose = True

    ip = args[0]

    return (ip, verbose)

def usage():
    print(r"""Telnet client class.
Usage: atelnet.py [-v] <IP>
       -v: enable verbose

Example 1):
>>> from atelnet import ATelnet
>>> with ATelnet('135.252.212.251') as tn:
>>>     rc, res = tn.run('ls /')
>>>     if rc:
>>>         for ln in res: print(ln)

Example 2):
-> { echo 'ls /'; echo 'ls /tmp'; } | ./atelnet.py 1.2.3.4

Example 3):
-> ./atelnet.py 1.2.3.4

""")
    sys.exit(1)

if __name__ == "__main__":
    ip, verbose = parse_args()
    with ATelnet(ip=ip, verbose=verbose) as tn:
        if tn.is_script_mode():
            tn.runloop()
        else:
            tn.interact()
