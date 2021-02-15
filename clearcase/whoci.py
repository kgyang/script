#!/usr/bin/env python

import os
import sys
import getopt
import subprocess

def usage():
    cmd = os.path.basename(sys.argv[0])
    print("Find who added/deleted CODE in FILE in BRANCH (main branch by default)")
    print("Usage: whoci.py <add|del> <CODE|LINERANGE> <FILE> [BRANCH]")
    print("CODE: code piece, LINERANGE: startline,endline")
    print("BRANCH example:")
    print("    main  - main branch")
    print("Example:")
    print("    whoci.py add 'int v = 1;' a.cc")
    print("    whoci.py add 22,25 a.cc")
    sys.exit(1)

def docmd(cmd):
    output = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (out, err) = output.communicate()
    return out

if (len(sys.argv) < 4): usage()
action = str(sys.argv[1])
code = str(sys.argv[2])
file = str(sys.argv[3])
branch = 'main'
if len(sys.argv) > 4:
    branch = str(sys.argv[4])

# verify
if not action in ('add', 'del'): usage()

if not os.getenv('CLEARCASE_ROOT'):
    print('select a view')
    sys.exit(1)

linerange = code.split(',')
if len(linerange) == 2 and linerange[0].isdigit() and linerange[1].isdigit():
    start = int(linerange[0])
    end = int(linerange[1])
    lines = open(file).readlines()
    if start < 1 or start > len(lines) or end < 1 or end > len(lines) or end < start:
        print('invalid line range')
        sys.exit(1)
    code = ''.join(lines[start-1:end])
    if not code:
        print('no code specified')
        sys.exit(1)

if not os.path.isfile(file):
    print(file, "does not exist")
    sys.exit(1)

# retrieve all history versions in given branch
cmd = 'cleartool lshistory -branch ' + branch + ' -short ' + file
vers = docmd(cmd).split()

# search the CODE from latest version to oldest
found = None
for ver in vers:
    vernum = ver.split('/')[-1]
    if not vernum.isdigit(): continue
    if int(vernum) <= 0: continue
    if not os.path.isfile(ver):
        print(ver, 'is not file')
        continue
    f = open(ver);
    if action == 'add':
        # who added: keep searching until the CODE is not found
        if f.read().find(code) == -1: break
    else:
        # who deleted: keep searching until the CODE is found
        if f.read().find(code) >= 0: break
    found = ver

if found:
    cmd = 'cleartool desc ' + found
    print(docmd(cmd))
else:
    print("not found")
    sys.exit(1)

