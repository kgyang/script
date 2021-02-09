#!/bin/env python
import os
import csv
import sys

def build(csvfile, pemfile):
    if not os.path.isfile(csvfile):
        sys.stderr.write(csvfile + ' does not exist, refer to https://wiki.mozilla.org/CA/Included_Certificates')
        sys.exit(1)
    with open(pemfile, 'w') as f:
        number = 0
        header = None
        for line in csv.reader(open(csvfile), delimiter=',', quotechar='"'):
            if header is None:
                if 'Owner' not in line or 'PEM Info' not in line: continue
                header = line
                OWNER_COL = header.index('Owner')
                CO_COL = header.index('Certificate Issuer Organization')
                OU_COL = header.index('Certificate Issuer Organizational Unit')
                CN_COL = header.index('Common Name or Certificate Name')
                SN_COL = header.index('Certificate Serial Number')
                SHA256_COL = header.index('SHA-256 Fingerprint')
                VALID_FROM_COL = header.index('Valid From [GMT]')
                VALID_TO_COL = header.index('Valid To [GMT]')
                PEM_COL = header.index('PEM Info')
            else:
                for field in (OWNER_COL, CO_COL, OU_COL, CN_COL, SN_COL, SHA256_COL, VALID_FROM_COL, VALID_TO_COL):
                    f.write(str("# ") + header[field] + (str(" = ") + line[field]).rstrip() + str('\n'))
                f.write(line[PEM_COL].strip("'") + str('\n\n'))
                number += 1
        if header is None:
            sys.stderr.write(csvfile + ' is invalid\n')
            sys.exit(1)
        print(pemfile + '(' + str(number) + ' certificates) is generated' )

def usage():
    sys.stderr.write('build trust anchor\n')
    sys.stderr.write('Usage: buildpem.py <csvfile> <pemfile>\n')
    sys.stderr.write("  - Input: <csvile>, Output: <pemfile>\n")
    sys.exit(1)

if __name__ == '__main__':
    if len(sys.argv) != 3: usage()
    build(sys.argv[1], sys.argv[2])
