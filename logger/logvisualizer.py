#!/usr/bin/env python

import sys
import os
import re
import gc
import threading
import time
import datetime


'''
10:33:52.106,1/1/12 tod txtime 1571312085000000000 rxtime 1571312085000000001
10:33:52.106,offset 1 delay 0
10:33:52.106,dco freqoffset -1000000000

06:18:35.400,2 dlyr seq 27785 intvl -4 cf 9961 t4 1580969951995108445 t3 1580969951995101729
06:18:35.459,2 sync seq 27233 intvl -4 cf 17975 t1 1580969952054748175 t2 1580969952054754889
06:18:35.459,offset -1 delay 6715
'''


LOG_SYNC = "sync"
LOG_DLYR = "dlyr"
LOG_TOD  = "tod"
LOG_OFFSET = "offset"
LOG_FREQOFFSET = "freqoffset"

T1 = "T1"
T2 = "T2"
T3 = "T3"
T4 = "T4"
CF = "CF"
TX = "TX"
RX = "RX"
OFFSET = "OFFSET"
DELAY = "DELAY"
FREQOFFSET = "FREQOFFSET"

PATH_DELAY = 0
VERBOSE = False
PARSERS = dict()
AXES = list()
DATE_START = int(time.mktime(datetime.datetime.now().date().timetuple()))

MAX_REALTIME_MINUTES = 2

class Bin(object):
    def __init__(self, time):
        self.time = time
        self.max = 0
        self.min = 0
        self.avg = 0

class Realtime(object):
    def __init__(self, time, val):
        self.time = time
        self.data = val

class PM(object):
    def __init__(self, stat_seconds=60):
        self.lock = threading.Lock()
        self.stat_seconds = stat_seconds
        self.max_bin_number = 7*24*60 # 7*24 hours
        self.max_realtime_number = 16*60*MAX_REALTIME_MINUTES
        self.samples = list()
        self.realtimelist= list()
        self.binlist = list()

    def addSample(self, time, data):
        global DATE_START
        self.lock.acquire()
        time += DATE_START
        if self.realtimelist and self.realtimelist[-1].time > time:
            time += 24*3600
            DATE_START += 24*3600

        if len(self.realtimelist) >= self.max_realtime_number:
            self.realtimelist = self.realtimelist[int(self.max_realtime_number/4):]
        self.realtimelist.append(Realtime(time, data))
        
        if not self.binlist or int(time/self.stat_seconds) > int(self.binlist[-1].time/self.stat_seconds):
            self.binlist.append(Bin(time))
            self.samples = list()
        if len(self.binlist) > self.max_bin_number:
            self.binlist.pop(0)

        self.samples.append(data)
        if self.binlist:
            self.binlist[-1].max = max(self.samples)
            self.binlist[-1].min = min(self.samples)
            self.binlist[-1].avg = int(sum(self.samples)/len(self.samples))
        self.lock.release()

    def getLatestSample(self):
        if self.samples: return self.samples[-1]
        else: return 0

    def getRealtimeList(self):
        self.lock.acquire()
        timelist = [ realtime.time for realtime in self.realtimelist ]
        datalist = [ realtime.data for realtime in self.realtimelist ]
        self.lock.release()
        return (timelist, datalist)

    def getBinList(self):
        self.lock.acquire()
        timelist = [ bin.time for bin in self.binlist ]
        maxlist = [ bin.max for bin in self.binlist ]
        minlist = [ bin.min for bin in self.binlist ]
        avglist = [ bin.avg for bin in self.binlist ]
        self.lock.release()
        return (timelist, maxlist, minlist, avglist)

class LogParser(object):
    def __init__(self, pattern, pmtypes):
        timepattern = r'(?P<hour>\d+):(?P<min>\d+):(?P<sec>\d+)\.(?P<msec>\d+),'
        self.pattern = re.compile(timepattern + pattern)
        self.time = 0
        self.PMs = dict()
        self.logs = 0
        for pm in pmtypes: self.PMs[pm] = PM()

    def getPM(self, pmtype):
        return self.PMs[pmtype]

    def getMatch(self, log):
        m = self.pattern.match(log)
        if m:
            self.logs += 1
            return m.groupdict()
        else:
            return dict()

    def getLogNumber(self):
        return self.logs

    def parseLog(self, log):
        pass

    @staticmethod
    def calculate_delay(t1, t2, t3, t4):
        return int((t2 - t1 + t4 - t3)/2)

    @staticmethod
    def calculate_offset(t1, t2, t3, t4):
        return int((t2 - t1 + t3 - t4)/2)
 
    @staticmethod
    def get_interval_ns(interval):
        if interval == 0x7F:
            return 62500000 # 1/16
        if interval < 0:
            return int(1000000000/(1<<(-1*interval)))
        else:
            return int(1000000000*(1<<interval))

    @staticmethod
    def get_delta(c, s, interval):
        return int(c - s - interval)

class SyncLogParser(LogParser):
    def __init__(self):
        super(SyncLogParser, self).__init__(\
r'(?P<port>[^ ]*) sync seq (?P<seq>\d+) intvl (?P<intvl>-?\d+) cf (?P<cf>\d+) t1 (?P<t1>\d+) t2 (?P<t2>\d+)',\
             [T1, T2, CF, OFFSET])
        self.start = None
        self.intervals = 0
        self.prev = None
        self.mstime = 0

    def parseLog(self, log):
        m = self.getMatch(log)
        if not m: return False

        interval = self.get_interval_ns(int(m['intvl']))
        time = int(m['hour'])*3600 + int(m['min'])*60 + int(m['sec']) + int(m['msec'])/1000.0
        mstime = int(m['hour'])*3600000 + int(m['min'])*60000 + int(m['sec'])*1000 + int(m['msec'])
        delta = mstime - self.mstime
        if self.mstime > 0 and delta < 30:
            print("delta time " + str(delta) + "ms")
            print(log)
        self.mstime = mstime

        if not self.start:
            self.start = m
        else:
            seqdiff = int(m['seq']) - int(self.prev['seq'])
            if seqdiff < 0: seqdiff += 65536
            if seqdiff != 1:
                sys.stderr.write(datetime.datetime.fromtimestamp(time + DATE_START).strftime("%Y-%m-%d %H:%M:%S")\
                                 + ', sync seq not continuous: cur ' + m['seq']  + ', pre ' + self.prev['seq']\
                                 + ', diff ' + str(seqdiff) + '\n')
            self.intervals += seqdiff*interval

        t1 = self.get_delta(int(m['t1']), int(self.start['t1']), self.intervals)
        t2 = self.get_delta(int(m['t2']), int(self.start['t2']), self.intervals)
        cf = self.get_delta(int(m['cf']), int(self.start['cf']), 0)

        self.getPM(T1).addSample(time, t1)
        self.getPM(T2).addSample(time, t2)
        self.getPM(CF).addSample(time, cf)
        if PATH_DELAY:
            offset = int(m['t2']) - int(m['t1']) - PATH_DELAY
            self.getPM(OFFSET).addSample(time, offset)

        # big jump from master
        if self.prev and abs(t1) > 10000:
            sys.stderr.write(datetime.datetime.fromtimestamp(time + DATE_START).strftime("%Y-%m-%d %H:%M:%S") + ', t1 jump ' + str(t1) +' ns, new sync start\n')
            self.start = m
            self.intervals = 0

        self.prev = m

class DlyrLogParser(LogParser):
    def __init__(self):
        super(DlyrLogParser, self).__init__(\
r'(?P<port>[^ ]*) dlyr seq (?P<seq>\d+) intvl (?P<intvl>-?\d+) cf (?P<cf>\d+) t4 (?P<t4>\d+) t3 (?P<t3>\d+)',\
              [T3, T4, CF, OFFSET])
        self.start = None
        self.intervals = 0
        self.prev = None

    def parseLog(self, log):
        m = self.getMatch(log)
        if not m: return False

        interval = self.get_interval_ns(int(m['intvl']))
        time = int(m['hour'])*3600 + int(m['min'])*60 + int(m['sec']) + int(m['msec'])/1000.0

        if not self.start:
            self.start = m
        else:
            seqdiff = int(m['seq']) - int(self.prev['seq'])
            if seqdiff < 0: seqdiff += 65536
            if seqdiff != 1:
                sys.stderr.write(datetime.datetime.fromtimestamp(time + DATE_START).strftime("%Y-%m-%d %H:%M:%S")\
                                 + ', dlyr seq not continuous: cur ' + m['seq']  + ', pre ' + self.prev['seq']\
                                 + ', diff ' + str(seqdiff) + '\n')
            self.intervals += seqdiff*interval

        t3 = self.get_delta(int(m['t3']), int(self.start['t3']), self.intervals)
        t4 = self.get_delta(int(m['t4']), int(self.start['t4']), self.intervals)
        cf = self.get_delta(int(m['cf']), int(self.start['cf']), 0)

        self.getPM(T3).addSample(time, t3)
        self.getPM(T4).addSample(time, t4)
        self.getPM(CF).addSample(time, cf)
        if PATH_DELAY:
            offset = int(m['t3']) - int(m['t4']) + PATH_DELAY
            self.getPM(OFFSET).addSample(time, offset)

        # big jump from master
        if self.prev and abs(t4) > 10000:
            sys.stderr.write(datetime.datetime.fromtimestamp(time + DATE_START).strftime("%Y-%m-%d %H:%M:%S") + ', t4 jump ' + str(t4) +' ns, new dlyr start\n')
            self.start = m
            self.intervals = 0

        self.prev = m

class ToDLogParser(LogParser):
    def __init__(self):
        super(ToDLogParser, self).__init__(\
r'(?P<port>[^ ]*) tod txtime (?P<tx>\d+) rxtime (?P<rx>-?\d+)',\
             [TX, RX])
        self.start = None
        self.intervals = 0
        self.prev = None

    def parseLog(self, log):
        m = self.getMatch(log)
        if not m: return False

        interval = self.get_interval_ns(0)
        time = int(m['hour'])*3600 + int(m['min'])*60 + int(m['sec']) + int(m['msec'])/1000.0

        if not self.start:
            self.start = m
        else:
            self.intervals += interval

        tx = self.get_delta(int(m['tx']), int(self.start['tx']), self.intervals)
        rx = self.get_delta(int(m['rx']), int(self.start['rx']), self.intervals)

        self.getPM(TX).addSample(time, tx)
        self.getPM(RX).addSample(time, rx)

        # big jump from master
        if self.prev and ( abs(tx) > 10000 or abs(rx) > 10000 ):
            sys.stderr.write(datetime.datetime.fromtimestamp(time + DATE_START).strftime("%Y-%m-%d %H:%M:%S") +
                             ', tx/rx jump ' + str(tx) + '/' + str(rx) + ' ns, new tod start\n')
            self.start = m
            self.intervals = 0

        self.prev = m

class OffsetLogParser(LogParser):
    def __init__(self):
        super(OffsetLogParser, self).__init__(r'offset (?P<offset>-?\d+) delay (?P<delay>-?\d+)', [OFFSET, DELAY])
        self.intervals = 0

    def parseLog(self, log):
        m = self.getMatch(log)
        if not m: return False

        time = int(m['hour'])*3600 + int(m['min'])*60 + int(m['sec']) + int(m['msec'])/1000.0
        self.getPM(OFFSET).addSample(time, int(m['offset']))
        self.getPM(DELAY).addSample(time, int(m['delay']))

class FreqOffsetLogParser(LogParser):
    def __init__(self):
        super(FreqOffsetLogParser, self).__init__(r'.*dco freqoffset (?P<freqoffset>-?\d+)', [FREQOFFSET])
        self.intervals = 0

    def parseLog(self, log):
        m = self.getMatch(log)
        if not m: return False

        time = int(m['hour'])*3600 + int(m['min'])*60 + int(m['sec']) + int(m['msec'])/1000.0
        self.getPM(FREQOFFSET).addSample(time, int(m['freqoffset'])/1000000000000.0)

class Axes(object):
    def __init__(self, ax, title, ylim=500):
        self.ax = ax
        self.title = title
        #ax.set_title(title, fontsize='x-small')
        ax.set_ylabel(title, fontsize='x-small')
        self.plots = dict()
        self.set_ylim(ylim)
        self.xleft = datetime.datetime.fromtimestamp(DATE_START)
        self.xright = self.xleft + datetime.timedelta(minutes=2, seconds=10)
        self.ax.set_xlim(left=self.xleft, right=self.xright)
        hfmt = dates.DateFormatter('%M:%S')
        self.ax.xaxis.set_major_formatter(hfmt)
        for tick in self.ax.xaxis.get_major_ticks(): tick.label.set_fontsize('x-small')
        for tick in self.ax.yaxis.get_major_ticks(): tick.label.set_fontsize('x-small')
        #ax.xaxis.set_major_locator(dates.MinuteLocator())
        ax.grid()

    def set_ylim(self, ylim):
        self.ylim = ylim
        if ylim > 100:
            self.ax.set_ylim(-1*ylim - 10, ylim + 10)
        else:
            self.ax.set_ylim(-1*ylim, ylim)

    def limit_y(self, yval):
        if self.ylim > 0:
            if yval < (-1*self.ylim): return int(-1*self.ylim)
            if yval > self.ylim: return int(self.ylim)
        return yval

    def updatePlots(self):
        pass

    def update_plot(self, plabel, timelist, ylist):
        n = len(timelist)
        if not n: return

        datelist = list(map(datetime.datetime.fromtimestamp, timelist))

        if self.xleft < datelist[0] or self.xright < datelist[-1]:
            self.xleft = datelist[0]
            delta = datelist[-1] - datelist[0]
            if delta <= datetime.timedelta(minutes=MAX_REALTIME_MINUTES, seconds=10):
                delta = datetime.timedelta(minutes=MAX_REALTIME_MINUTES, seconds=10)
            else:
                delta = datetime.timedelta(days=delta.days,\
                        seconds=(delta.seconds - (delta.seconds%1800) + 1800))

            self.xright = self.xleft + delta
            self.ax.set_xlim(left=self.xleft, right=self.xright)

        if len(datelist) > 1:
            if (datelist[-1] - datelist[-2]) < datetime.timedelta(seconds=2):
                self.ax.xaxis.set_major_formatter(dates.DateFormatter('%M:%S'))
            else:
                self.ax.xaxis.set_major_formatter(dates.DateFormatter('%H-%M'))

        if plabel not in self.plots:
            self.plots[plabel] = self.ax.plot(datelist, ylist, label=plabel, linewidth=0.6)[0]
        else:
            self.plots[plabel].set_xdata(datelist)
            self.plots[plabel].set_ydata(ylist)
        self.plots[plabel].set_label(plabel + "["\
                                     + str(min(ylist)) + ","\
                                     + str(max(ylist))\
                                     + "]")
        self.ax.legend(loc='upper left', ncol=len(self.plots), fontsize='x-small', shadow=False)

class RealtimeAxes(Axes):
    def __init__(self, ax, title, logger, pmtypes, ylim=500):
        super(RealtimeAxes, self).__init__(ax, title, ylim)
        self.logger = logger
        self.pmtypes = pmtypes

    def updatePlots(self):
        for pm in self.pmtypes:
            timelist, dlist = self.logger.getPM(pm).getRealtimeList()
            self.update_plot(str(pm), timelist, dlist)
        self.ax.set_ylabel(self.title + "\n(" + str(self.logger.getLogNumber()) + ")", fontsize='x-small')

class StatAxes(Axes):
    def __init__(self, ax, name, logger, pmtypes, ylim=500):
        super(StatAxes, self).__init__(ax, name, ylim)
        self.logger = logger
        self.pmtypes = pmtypes

    def updatePlots(self):
        for pm in self.pmtypes:
            timelist, maxlist, minlist, avglist = self.logger.getPM(pm).getBinList()
            label = str(pm)
            if len(self.pmtypes) == 1: label = ''
            self.update_plot(label+'max', timelist, maxlist)
            self.update_plot(label+'min', timelist, minlist)
            self.update_plot(label+'avg', timelist, avglist)

def save_bin_to_file(f, name, datalists):
    f.write('\n' + name + ':\n')
    f.write('--------\n')
    for i in range(0, len(datalists[0])):
        f.write(' '.join([ str(int(datalist[i])) for datalist in datalists ]) + '\n')

def save_results():
    now = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    global PARSERS
    with open('visualizerresult.log', 'a') as f:
        f.write('\n' + now + '\n')
        f.write('===================\n')
        for parser in PARSERS.values():
            if isinstance(parser, SyncLogParser):
                save_bin_to_file(f, 't1 stat', parser.getPM(T1).getBinList())
                save_bin_to_file(f, 't2 stat', parser.getPM(T2).getBinList())
            if isinstance(parser, DlyrLogParser):
                save_bin_to_file(f, 't3 stat', parser.getPM(T3).getBinList())
                save_bin_to_file(f, 't4 stat', parser.getPM(T4).getBinList())
            if isinstance(parser, OffsetLogParser):
                save_bin_to_file(f, 'offset stat', parser.getPM(OFFSET).getBinList())


def read_file(logfile):
    with open(logfile) as f:
        # estimate total line number by assuming 68 bytes per line
        # read total file in 1 minutes
        fsize = os.stat(logfile).st_size
        linebulk = int((fsize/68)/60)
        if linebulk < 2000: linebulk = 2000
        sys.stderr.write('read ' + str(linebulk) + ' lines per 0.5 second\n')
        n = 0
        for log in f:
            read_log(log)
            n += 1
            if n%linebulk == 0:
                time.sleep(0.5)

def read_input():
    while True:
        log = sys.stdin.readline()
        if not len(log): break
        read_log(log)

def read_from_logger(logger):
    while True:
        log = logger.readline()
        if not log: break
        read_log(log)

def read_log(log):
    global PARSERS
    global VERBOSE
    for parser in PARSERS.values():
        if parser.parseLog(log): break
    update_path_delay()
    if VERBOSE:
        print(log)

def update_path_delay():
    global PATH_DELAY

    if PATH_DELAY: return

    offset = PARSERS[LOG_OFFSET].getPM(OFFSET).getLatestSample()
    delay = PARSERS[LOG_OFFSET].getPM(DELAY).getLatestSample()

    if offset > 10000: return
    if delay == 0: return

    PATH_DELAY = delay

    sys.stderr.write('Path delay: ' + str(PATH_DELAY) + '\n')


def update_plot(frame):
    global AXES
    for axes in AXES:
        axes.updatePlots()
    # workaround as per link: https://github.com/matplotlib/matplotlib/issues/8528
    # forcing gc to avoid memory leak due to matplotlib bug
    if frame%10 == 0:
        gc.collect()

def usage():
    cmd = os.path.basename(sys.argv[0])
    sys.stderr.write('plot realtime PTP timestamp information by reading log or connecting MACHINE\n')
    sys.stderr.write('Usage: ' + cmd + ' [-l sync|dlyr|tod|offset|freqoffset] [-v] [-f logfile] [-t <hours>]\n')
    sys.stderr.write('-l: specify type of log to be parsed and shown\n')
    sys.stderr.write('-f: specify logfile to be played back\n')
    sys.stderr.write('-v: verbose mode, in which script will print received log\n')
    sys.exit(1)

if __name__ == '__main__':
    import os
    import getopt
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'l:f:n:S:s:tv')
    except getopt.error:
        usage()

    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    import matplotlib.dates as dates

    logtype = ''
    logfile = ''
    hours = 24

    for o, a in optlist:
        if o == '-l': logtype = str(a)
        if o == '-f': logfile = str(a)
        if o == '-t': hours = int(a)
        if o == '-v': VERBOSE = True

    if logtype and logtype not in ('sync', 'dlyr', 'tod', 'offset', 'freqoffset'): help()

    if logfile and not os.path.isfile(logfile):
        sys.stderr.write(str(logfile) + " not exist\n")
        sys.exit(1)

    if logfile and not logtype:
        with open(logfile) as f:
            for log in f:
                if log.find('sync') != -1 or log.find('dlyr') != -1: break
                if log.find('txtime') != -1:
                    logtype = LOG_TOD
                    break

    fig = plt.figure(1)

    if logtype: fig.suptitle(logtype.upper() + ' Visualizer')
    else: fig.suptitle('PTP Visualizer')
    
    if logtype == LOG_FREQOFFSET: MAX_REALTIME_MINUTES = 5

    PARSERS = {LOG_SYNC:SyncLogParser(),\
               LOG_DLYR:DlyrLogParser(),\
               LOG_TOD:ToDLogParser(),\
               LOG_OFFSET:OffsetLogParser(),\
               LOG_FREQOFFSET:FreqOffsetLogParser()}

    if logtype == LOG_SYNC:
        AXES = [\
            RealtimeAxes(plt.subplot(3,2,1), 'T1',         PARSERS[LOG_SYNC], [T1]),\
            StatAxes(plt.subplot(3,2,2),     'T1 Stat',    PARSERS[LOG_SYNC], [T1]),\
            RealtimeAxes(plt.subplot(3,2,3), 'T2',         PARSERS[LOG_SYNC], [T2]),\
            StatAxes(plt.subplot(3,2,4),     'T2 Stat',    PARSERS[LOG_SYNC], [T2]),\
            RealtimeAxes(plt.subplot(3,2,5), 'T2-T1',      PARSERS[LOG_SYNC], [OFFSET]),\
            StatAxes(plt.subplot(3,2,6),     'T2-T1 Stat', PARSERS[LOG_SYNC], [OFFSET])]
    elif logtype == LOG_DLYR:
        AXES = [\
            RealtimeAxes(plt.subplot(3,2,1), 'T3',         PARSERS[LOG_DLYR], [T3]),\
            StatAxes(plt.subplot(3,2,2),     'T3 Stat',    PARSERS[LOG_DLYR], [T3]),\
            RealtimeAxes(plt.subplot(3,2,3), 'T4',         PARSERS[LOG_DLYR], [T4]),\
            StatAxes(plt.subplot(3,2,4),     'T4 Stat',    PARSERS[LOG_DLYR], [T4]),\
            RealtimeAxes(plt.subplot(3,2,5), 'T3-T4',      PARSERS[LOG_DLYR], [OFFSET]),\
            StatAxes(plt.subplot(3,2,6),     'T3-T4 Stat', PARSERS[LOG_DLYR], [OFFSET])]
    elif logtype == LOG_OFFSET:
        AXES = [\
            RealtimeAxes(plt.subplot(2,1,1), 'OFFSET',      PARSERS[LOG_OFFSET], [OFFSET]),\
            StatAxes(plt.subplot(2,1,2),     'OFFSET Stat', PARSERS[LOG_OFFSET], [OFFSET])]
    elif logtype == LOG_TOD:
        AXES = [\
            StatAxes(plt.subplot(2,2,1),     'TX Stat',     PARSERS[LOG_TOD], [TX]),\
            StatAxes(plt.subplot(2,2,2),     'RX Stat',     PARSERS[LOG_TOD], [RX]),\
            RealtimeAxes(plt.subplot(2,2,3), 'OFFSET',      PARSERS[LOG_OFFSET], [OFFSET]),\
            StatAxes(plt.subplot(2,2,4),     'OFFSET Stat', PARSERS[LOG_OFFSET], [OFFSET])]
    elif logtype == LOG_FREQOFFSET:
        AXES = [\
            RealtimeAxes(plt.subplot(3,1,1), 'FREQOFFSET',  PARSERS[LOG_FREQOFFSET], [FREQOFFSET], 0.2), \
            RealtimeAxes(plt.subplot(3,1,2), 'OFFSET',      PARSERS[LOG_OFFSET], [OFFSET], 100),\
            StatAxes(plt.subplot(3,1,3),     'FREQOFFSET Stat', PARSERS[LOG_FREQOFFSET], [FREQOFFSET], 0.2)]
    else:
        AXES = [\
            RealtimeAxes(plt.subplot(2,2,1), 'SYNC',        PARSERS[LOG_SYNC], [T1,T2]),\
            RealtimeAxes(plt.subplot(2,2,2), 'DLYR',        PARSERS[LOG_DLYR], [T3,T4]),\
            RealtimeAxes(plt.subplot(2,2,3), 'OFFSET',      PARSERS[LOG_OFFSET], [OFFSET]),\
            StatAxes(plt.subplot(2,2,4),     'OFFSET Stat', PARSERS[LOG_OFFSET], [OFFSET])]

    ani = animation.FuncAnimation(fig, update_plot, interval=3000, save_count=0, repeat=False)

    reader = None
    if logfile:
        reader = threading.Thread(target=read_file, args=(logfile,))
    else:
        reader = threading.Thread(target=read_input)
    reader.start()

    plt.show()

    save_results()
