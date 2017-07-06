#!/usr/bin/env python 
import os
import sys
import getpass
import time
import telnetlib
import ftplib

TIMEOUT = 10
def usage():
    cmd = os.path.basename(sys.argv[0])
    print('Usage:')
    if sys.platform[:3] == 'win':
        print('set HOST_PASSWORD=xxxxxx')
    else:
        print('export HOST_PASSWORD=xxxxxx')
    print(cmd + ' HOST VIEW')
    sys.exit(1)

def doshellcmd(tn, cmd):
    if not tn: return None
    try:
        tn.write(cmd + '\n')
        result = tn.expect([r'\r\n-> '], TIMEOUT)
        if result[0] == -1:
            print("'" + cmd + "' timeout")
            tn.close()
            sys.exit(1)
        else:
            return result[2].splitlines()[:-2] # remove last two lines (prompt)
    except EOFError, detail:
        print("'" + cmd + "' fail: " + detail)
        tn.close()
        sys.exit(1)

def readallresponse(tn):
    try:
        data = str()
        # check 
        delay = 0
        while delay < TIMEOUT:
            data = tn.read_very_eager()
            if data: break
            time.sleep(1)
            delay += 1
        if delay == TIMEOUT:
            print('no data')
            return data
        # read all
        delay = 0
        while delay < TIMEOUT:
            time.sleep(2)
            delay += 2
            more = tn.read_very_eager()
            if not more: break
            data += more
        if delay >= TIMEOUT: print('too many data')
        return data
    except EOFError, detail:
        print('read data error: ' + detail)
        tn.close()
        sys.exit(1)

def telnetlogin(host, port, user, password):
    tn = telnetlib.Telnet(host, port)
    if not tn:
        print('connect fail')
        sys.exit(1)
    #tn.set_debuglevel(1)
    try:
        if not tn.read_until('login: ', TIMEOUT).endswith('login: '):
            raise NameError('username timeout')
        tn.write(user + "\n")
        if not tn.read_until('Password: ', TIMEOUT).endswith('Password: '):
            raise NameError('password timeout')
        tn.write(password + "\n")
        # clean output
        res = readallresponse(tn)
        if not res:
            raise NameError('prompt timeout')
        if res.endswith('login: '):
            raise NameError('incorrect password')
        # do not echo input to facilitate parsing output
        doshellcmd(tn, 'stty -echo')
    except (EOFError, NameError), detail:
        print("login fail: " + detail)
        tn.close()
        sys.exit(1)
    return tn

def telnetlogout(tn):
    tn.write('exit\n')
    tn.close()

#if sys.platform[:3] != 'win':
#  print('only allowed to be run on window platform')
#  sys.exit(1)

if len(sys.argv) != 3: usage()
host = sys.argv[1]
view = sys.argv[2]
port = 23

user = view.split('-')[0]
password = os.getenv('HOST_PASSWORD')

rootdir = ''
if not rootdir:
    cwd = os.getcwd()
    if os.path.isdir(cwd + 'vobs'):
        rootdir = cwd
    else:
        idx = cwd.find('vobs')
        if idx == -1:
            print('project root directory not found')
            print('please go to root directory (subdir must be vobs) then run again')
            sys.exit(1)
        rootdir = cwd[0:idx]

if not user:
    sys.stdout.write('username: ')
    sys.stdout.flush()
    user = sys.stdin.readline().rstrip('\r\n')
else:
    print('username: ' + user)

if not password:
    password = getpass.getpass('HOST_PASSWORD not defined, please enter password: ')

# login HOST
sys.stdout.write('\ntelnet ' + host + '...')
sys.stdout.flush()
tn = telnetlogin(host, port, user, password)
if not tn:
    print('fail')
    sys.exit(1)
print('success')

# set view on HOST
sys.stdout.write('\nsetview ' + view + '...')
sys.stdout.flush()
tn.write('cleartool setview ' + view + '\n')
readallresponse(tn)
if not doshellcmd(tn, 'echo $CLEARCASE_ROOT')[0]:
    print('not found')
    telnetlogout(tn)
    sys.exit(1)
print('success')

# get check-out file list from HOST:VIEW
print('\ncheck-out files in ' + view + ':')
co = doshellcmd(tn, 'lsco')[1:]
if not co:
    print('no checkout files')
    telnetlogout(tn)
    sys.exit(1)
for file in co:
    print(file)

# upload local files corresponding to check-outs to HOME@HOST
sys.stdout.write('\nftp ' + host + '...')
ftp = ftplib.FTP(host, user, password)
if not ftp:
    print('fail')
    telnetlogout(tn)
    sys.exit(1)
print('success, upload files to ' + host + '/home/' + user)
for file in co:
    fname = os.path.normpath(rootdir + file)
    if not os.path.isfile(fname):
        print(fname + ' not found')
        continue
    print(fname)
    cmd = 'STOR ' + ':'.join(file.split('/')) # rename file to avoid name conflict
    ftp.storbinary(cmd, open(fname))
ftp.quit()

# update check-out files in HOST:VIEW by local files uploaded to HOME@HOST
print('\nlist of files updated:')
cmd= r'''for f in $(lsco)
do
tf=~/${f//\//:}
[ -f $tf ] || { echo $f upload failed; continue; }
dos2unix -q $tf
[ -w $f ] && ! cmp -s $tf $f && { cp $f $f.keep; cp $tf $f; echo $f; }
rm -f $tf
done'''
res = doshellcmd(tn, cmd)
for file in res[1:]:
    print(file)

# quit from view
doshellcmd(tn, 'exit')

# logout from linux box
telnetlogout(tn)

