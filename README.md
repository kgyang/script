<h1>USER GUIDE FOR SCRIPTS</h1>
(Note: This document is generated by common/genreadme)<br>

<h2>clearcase/updateremoteco.py</h2>
    update source code from local PC to specified clearcase view in remote machine
    Usage:
    set HOST_PASSWORD=xxxxxx
    updateremoteco.py HOST VIEW

<h2>clearcase/whoci.py</h2>
    Find who added/deleted CODE in FILE in BRANCH (main branch by default)
    Usage: whoci.py <add|del> <CODE|LINERANGE> <FILE> [BRANCH]
    CODE: code piece, LINERANGE: startline,endline
    BRANCH example:
    main - main branch
    Example:
    whoci.py add 'int v = 1;' a.cc
    whoci.py add 22,25 a.cc

<h2>common/bid.py</h2>
    automatic bid for shanghai license (for fun)

<h2>common/codestat</h2>
    ./codestat <file1> <file2>
    identical to "diff -u diff1 diff2 | diffstat

<h2>common/codesync</h2>
    sync source code between two git repositories
    Usage: codesync <to|from> <remote>

<h2>common/download_cs143</h2>
    download cs143(compilers design) pdf documents listed in the page

<h2>common/genreadme</h2>
    generate README.md

<h2>common/itoa</h2>
    translate hex integer to string
    Usage:
    1) echo '31 be' | itoa
    2) ./itoa 32 be

<h2>common/itoa.py</h2>
    translate hex integer to string.
    Usage:
    1) echo '31 be' | ./itoa.py
    2) ./itoa.py 32 be

<h2>common/prune_binary</h2>
    remove unprintable in files
    Usage: prune_binary <file...>

<h2>common/rm_trailing_space</h2>
    remove trailing white space in file
    Usage: ./rm_trailing_space <file...>

<h2>common/rmcomments</h2>
    remove c/c++ comments
    Usage: rmcomments <file...>

<h2>common/sendmail.py</h2>
    sendmail utility

<h2>cpu/cpu_usage_monitor</h2>
    cpu usage monitor

<h2>cpu/process_cpu_usage</h2>
    print process cpu usage
    Usage: ./process_cpu_usage <processname>

<h2>git/git-cppcheck</h2>
    This script prints out cppcheck results of code changes.
    The code changes could be uncommitted (by default) or commit specified.
    It returns 1 if there're error or warning reports.
    
    Usage: git-cppcheck [<commit|file>...]
    
    Examples:
    git-cppcheck -- check uncommitted code changes
    git-cppcheck HEAD -- check code changes in latest commit
    git-cppcheck 03c58d -- check code changes in commit
    git-cppcheck *.cc -- check files

<h2>git/git_ls</h2>
    list all changed/new files in a commit
    Usage: ./git_ls [commit]

<h2>git/gt_whoci</h2>
    find out the commit which made the given code change
    Usage: gt_whoci <text> <file>

<h2>logger/logvisualizer.py</h2>
    plot realtime PTP timestamp information by reading log or connecting MACHINE
    Usage: logvisualizer.py [-l sync|dlyr|tod|offset|freqoffset] [-v] [-f logfile] [-t <hours>]
    -l: specify type of log to be parsed and shown
    -f: specify logfile to be played back
    -v: verbose mode, in which script will print received log

<h2>logger/rlogger</h2>
    This script is used to read log from fifo in remote machine
    Usage: rlogger -n <IP> [-t <HOURS>]
    -m: master mode, in which script will close fifo before exit

<h2>logger/rlogger_ssh</h2>
    This script is used to read log from fifo on remote machine
    Usage: rlogger_ssh [-t <HOURS>] -n <IP>
    -t: specify run time (hours), 24 hours by default

<h2>logger/rlogger_ssh_simple</h2>
    This script is used to read log from remote machine without time limitation
    Usage: rlogger_ssh_simple <IP>

<h2>network/atelnet.py</h2>
    Telnet client class.
    Usage: atelnet.py [-v] <IP>
    -v: enable verbose
    
    Example 1):
    >>> from atelnet import ATelnet
    >>> with ATelnet('135.252.212.251') as tn:
    >>> rc, res = tn.run('ls /')
    >>> if rc:
    >>> for ln in res: print(ln)
    
    Example 2):
    -> { echo 'ls /'; echo 'ls /tmp'; } | ./atelnet.py 1.2.3.4
    
    Example 3):
    -> ./atelnet.py 1.2.3.4

<h2>network/cli.py</h2>
    CLI client class.
    Usage: cli.py [-v] <MACHINE>
    -v: enable verbose'
    Example 1):
    >>> from cli import Cli
    >>> with Cli('1.2.3.4') as cli:
    >>> rc, res = cli.run('help')
    >>> if rc:
    >>> for ln in res: print(ln)
    
    Example 2):
    -> { echo 'help'; } | ./cli.py 1.2.3.4
    
    Example 3):
    -> ./cli.py 1.2.3.4

<h2>network/itelnet.py</h2>
    Telnet client class for innet.
    Usage: itelnet.py [-v] <IP> <INNETC> <INNETD> [<LOGIN> <PASSWORD>]
    -v: enable verbose
    
    Example 1):
    >>> from itelnet import ITelnet
    >>> lc = ITelnet('1.2.3.4', 1, 19)
    >>> rc, res = lc.run('ls /')
    >>> if rc:
    >>> for ln in res: print(ln)
    
    Example 2):
    -> { echo 'ls /'; echo 'ls /tmp'; } | ./itelnet.py 1.2.3.4 1 19
    
    Example 3):
    -> ./itelnet.py 1.2.3.4 1 19
    -> ./itelnet.py 1.2.3.4 1 2 username password

<h2>network/rftp</h2>
    get/put files from/to peer server
    Usage: rftp <get|put> <filename>...

<h2>network/rsftp</h2>
    get/put files from/to peer server via sftp
    Usage: rsftp <get|put> <filename>...

<h2>trustanchor/buildpem.py</h2>
    build trust anchor
    Usage: buildpem.py <csvfile> <pemfile>
    - Input: <csvile>, Output: <pemfile>

<h2>trustanchor/verifypem</h2>
    verfiy trust anchor via SHA-256 calculation
    Usage: verifypem <pemfile>

<h2>vps/blockip.sh</h2>
    block ip listed in txt by iptables
    Usage: ./blockip.sh <start|stop>

