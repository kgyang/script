#!/bin/python

import sys

def usage():
    print(r"""translate hex integer to string.
Usage:
1) echo '31 be' | ./itoa.py
2) ./itoa.py 32 be""")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) < 2: usage()
    if sys.argv[1] == "-h": usage()
    for c in sys.argv[1:]: sys.stdout.write("%c" % int(c,16))
else:
    for c in sys.stdin.read().split(): sys.stdout.write("%c" % int(c,16))
print
