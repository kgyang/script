#!/usr/bin/python

UP_CONNECTOR_N1 = 1001
UP_CONNECTOR_N2 = 1002
UP_CONNECTOR_N3 = 1003
DOWN_CONNECTOR_N1 = 2001
DOWN_CONNECTOR_N2 = 2002
DOWN_CONNECTOR_N3 = 2003

PSS8_SHELF_BACKPLANE = (
(2, UP_CONNECTOR_N1, 3, UP_CONNECTOR_N1),
(2, UP_CONNECTOR_N2, 4, UP_CONNECTOR_N2),
(2, UP_CONNECTOR_N3, 5, UP_CONNECTOR_N3),
(3, UP_CONNECTOR_N3, 4, UP_CONNECTOR_N3),
(3, UP_CONNECTOR_N2, 5, UP_CONNECTOR_N2),
(4, UP_CONNECTOR_N1, 5, UP_CONNECTOR_N1),

(2, DOWN_CONNECTOR_N1, 3, DOWN_CONNECTOR_N1),
(2, DOWN_CONNECTOR_N2, 4, DOWN_CONNECTOR_N2),
(2, DOWN_CONNECTOR_N3, 5, DOWN_CONNECTOR_N3),
(3, DOWN_CONNECTOR_N3, 4, DOWN_CONNECTOR_N3),
(3, DOWN_CONNECTOR_N2, 5, DOWN_CONNECTOR_N2),
(4, DOWN_CONNECTOR_N1, 5, DOWN_CONNECTOR_N1),

(2, DOWN_CONNECTOR_N1, 21, DOWN_CONNECTOR_N1),
(2, DOWN_CONNECTOR_N2, 22, DOWN_CONNECTOR_N2),
(2, DOWN_CONNECTOR_N3, 23, DOWN_CONNECTOR_N3),
(3, DOWN_CONNECTOR_N3, 22, DOWN_CONNECTOR_N3),
(3, DOWN_CONNECTOR_N2, 23, DOWN_CONNECTOR_N2),
(4, DOWN_CONNECTOR_N1, 23, DOWN_CONNECTOR_N1),

(20, DOWN_CONNECTOR_N1, 21, DOWN_CONNECTOR_N1),
(20, DOWN_CONNECTOR_N2, 22, DOWN_CONNECTOR_N2),
(20, DOWN_CONNECTOR_N3, 23, DOWN_CONNECTOR_N3),
(21, DOWN_CONNECTOR_N3, 22, DOWN_CONNECTOR_N3),
(21, DOWN_CONNECTOR_N2, 23, DOWN_CONNECTOR_N2),
(22, DOWN_CONNECTOR_N1, 23, DOWN_CONNECTOR_N1)
)


CARD_20P_BP1 = 21 
CARD_20P_BP2 = 22 
CARD_20P_MATE_BP = 31
CARD_20P_C1 = 1
CARD_20P_C2 = 2
CARD_20P_C3 = 3
CARD_20P_C4 = 4
CARD_20P_C5 = 5
CARD_20P_C6 = 6
CARD_20P_C7 = 7
CARD_20P_C8 = 8
CARD_20P_C9 = 9
CARD_20P_C10 = 10
CARD_20P_C11 = 11
CARD_20P_C12 = 12
CARD_20P_C13 = 13
CARD_20P_C14 = 14
CARD_20P_C15 = 15
CARD_20P_C16 = 16
CARD_20P_C17 = 17
CARD_20P_C18 = 18
CARD_20P_C19 = 19
CARD_20P_C20 = 20

CARD_20P200_SWITCH = (
(UP_CONNECTOR_N1, UP_CONNECTOR_N2, CARD_20P_BP1),
(CARD_20P_BP1, CARD_20P_MATE_BP,
 CARD_20P_C1, CARD_20P_C2, CARD_20P_C3, CARD_20P_C4, CARD_20P_C5, CARD_20P_C6, CARD_20P_C7, CARD_20P_C8, CARD_20P_C9, CARD_20P_C10),
(CARD_20P_BP2, CARD_20P_MATE_BP,
 CARD_20P_C11, CARD_20P_C12, CARD_20P_C13, CARD_20P_C14, CARD_20P_C15, CARD_20P_C16, CARD_20P_C17, CARD_20P_C18, CARD_20P_C19, CARD_20P_C20),
(DOWN_CONNECTOR_N1, DOWN_CONNECTOR_N2, CARD_20P_BP2)
)

CARD_20P200_SWITCH_LAYOUT = (
(0, (CARD_20P_BP1, "ILK"), 1, (CARD_20P_BP1, "ILK")),
(1, (CARD_20P_MATE_BP, "ILK"), 2, (CARD_20P_MATE_BP, "ILK")),
(2, (CARD_20P_BP2, "ILK"), 3, (CARD_20P_BP2, "ILK"))
)

CARD_12P_C1 = 1
CARD_12P_C2 = 2
CARD_12P_C3 = 3
CARD_12P_C4 = 4
CARD_12P_C5 = 5
CARD_12P_C6 = 6
CARD_12P_C7 = 7
CARD_12P_C8 = 8
CARD_12P_C9 = 9
CARD_12P_C10 = 10
CARD_12P_C11 = 11
CARD_12P_C12 = 12
CARD_12P_BP1 = 21 

CARD_12P120_DESC = (
(UP_CONNECTOR_N1, DOWN_CONNECTOR_N2, CARD_12P_BP1),
(CARD_12P_BP1, 
 CARD_12P_C1, CARD_12P_C2, CARD_12P_C3, CARD_12P_C4, CARD_12P_C5, CARD_12P_C6,
 CARD_12P_C7, CARD_12P_C8, CARD_12P_C9, CARD_12P_C10, CARD_12P_C11, CARD_12P_C12))


class MultiGraph:
    def __init__(self):
        self.edges = dict()

    def addEdge(self, u, v, key):
        if u in self.edges:
            if v in self.edges[u]:
                self.edges[u][v].add(key)
            else:
                self.edges[u][v] = set([key])
        else:
            self.edges[u] = {v:set([key])}

        if v in self.edges:
            if u in self.edges[v]:
                self.edges[v][u].add(key)
            else:
                self.edges[v][u] = set([key])
        else:
            self.edges[v] = {u:set([key])}

    def removeEdge(self, u, v, key):
        self.edges[u][v].remove(key)
        self.edges[v][u].remove(key)
        if not self.edges[u][v]: del self.edges[u][v]
        if not self.edges[u]: del self.edges[u]
        if not self.edges[v][u]: del self.edges[v][u]
        if not self.edges[v]: del self.edges[v]

    def getEdges(self):
        return self.edges

    def findSimplePaths(self, u, v, path, paths):
        path.append(u)
        if u == v:
            paths.append(list(path)) # note: path is copied here
            path.pop()
            return
        if not u in self.edges:
            path.pop()
            return
        for tv in self.edges[u]:
            if tv in path: continue
            self.findSimplePaths(tv, v, path, paths)
        path.pop()

    def findMultiplePaths(self, pos, path, multipath, multipaths):
        if not path: return
        if pos == (len(path) - 1):
            multipath.append(path[pos])
            multipaths.append(list(multipath)) # note: multipath is copied here
            multipath.pop()
            return
        u = path[pos]
        v = path[pos+1]
        multipath.append(u)
        for key in self.edges[u][v]:
            multipath.append(key)
            self.findMultiplePaths(pos+1, path, multipath, multipaths)
            multipath.pop()
        multipath.pop()
            
    def findPaths(self, u, v):
        path = list()
        paths = list()
        self.findSimplePaths(u, v, path, paths)
        multipath = list()
        multipaths = list()
        for path in paths:
            self.findMultiplePaths(0, path, multipath, multipaths)
        return multipaths

class XC:
    def __init__(self, sshelf, sslot, sport, schan, dshelf, dslot, dport, dchan, protection, rate):
        self.sshelf = sshelf
        self.sslot  = sslot
        self.sport  = sport
        self.schan  = schan
        self.dshelf = dshelf
        self.dslot  = dslot
        self.dport  = dport
        self.dchan  = dchan
        self.protection = protection
        self.rate = rate

    def __str__(self):
        if self.protection: p = 'P'
        else: p = 'W'
        str = "%d/%d/%d/%d -> %d/%d/%d/%d(%s, %d)" % (self.sshelf, self.sslot, self.sport, self.schan, \
                                                      self.dshelf, self.dslot, self.dport, self.dchan, \
                                                      p, self.rate)
        return str

    def __eq__(self, other):
        return self.sshelf == other.sshelf and self.sslot == other.sslot and \
               self.sport == other.sport and self.schan == other.schan and \
               self.dshelf == other.dshelf and self.dslot == other.dslot and \
               self.dport == other.dport and self.dchan == other.dchan and \
               self.protection == other.protection and self.rate == other.rate

class SwitchXC:
    def __init__(self, shelf, slot, sport, schan, dport, dchan):
        self.shelf = shelf
        self.slot = slot
        self.sport = sport
        self.schan = schan
        self.dport = dport
        self.dchan = dchan

    def __str__(self):
        str = "%d/%d: %d/%d -> %d/%d" % (self.shelf, self.slot, \
                                         self.sport, self.schan, self.dport, self.dchan)
        return str

class Channel:
    def __init__(self, scnt, dcnt, rate):
        self.scnt = scnt 
        self.dcnt = dcnt
        self.rate = rate

class Switch:
    def __init__(self, card, ports):
        self.card = card
        self.switchxcdb = dict()
        self.chandb = dict()
        self.ports = ports
        for port in ports:
            self.switchxcdb[port] = dict()
            self.chandb[port] = dict()

    def hasPort(self, port):
        return (port in self.ports)

    def getPorts(self):
        return self.switchxcdb.iterkeys()

    def findChannel(self, sport, schan, dport, xc):
        if sport >= UP_CONNECTOR_N1 and dport >= UP_CONNECTOR_N1: return None
        if dport >= UP_CONNECTOR_N1:
            if self.card.getPortType(sport) == 'ILK' and self.getPortRate(sport) > 0 and self.getPortRate(dport) == 0: return None
        if sport >= UP_CONNECTOR_N1:
            if self.card.getPortType(dport) == 'ILK' and self.getPortRate(dport) > 0 and self.getPortRate(sport) == 0: return None
        if dport >= UP_CONNECTOR_N1 or sport >= UP_CONNECTOR_N1:
            return schan

        maxchannumber = 0
        maxrate = 0
        if self.card.getPortType(dport) == 'ILK':
            maxchannumber = 80
            maxrate = 120000

        for dchan in range(1, maxchannumber+1):
            if self.hasSwitchXC(sport, schan, dport, dchan): return dchan

        if xc.protection:
            for dchan in range(1, maxchannumber+1):
                swxc = self.getSwitchXC(dport, dchan, False)
                if swxc:
                    for ixc in swxc[3]:
                        if ixc.dshelf == xc.dshelf and ixc.dslot == xc.dslot and ixc.dport == xc.dport and ixc.dchan == xc.dchan:
                            return dchan

        swxc = self.getSwitchXC(sport, schan, xc.protection)
        if swxc:
            for ixc in swxc[3]:
                if ixc.dshelf == xc.sshelf and ixc.dslot == xc.sslot and ixc.dport == xc.sport and ixc.dchan == xc.schan and \
                   ixc.sshelf == xc.dshelf and ixc.sslot == xc.dslot and ixc.sport == xc.dport and ixc.schan == xc.dchan and \
                   not self.getSwitchXC(swxc[0], swxc[1], xc.protection):
                    return swxc[1]

        for dchan in range(1,maxchannumber+1):
            if self.getChannelRate(dport, dchan) == 0 and (self.getPortRate(dport) + xc.rate) <= maxrate:
                return dchan

        for dchan in range(1,maxchannumber+1):
            if not self.getSwitchXC(dport, dchan, xc.protection) and self.getChannelRate(dport, dchan) > 0:
                return dchan
        return None

    def hasSwitchXC(self, sport, schan, dport, dchan):
        switchxc = self.getSwitchXC(dport, dchan, True)
        if switchxc and switchxc[0:2] == (sport, schan): return True
        switchxc = self.getSwitchXC(dport, dchan, False)
        if switchxc and switchxc[0:2] == (sport, schan): return True
        return False

    def getSwitchXC(self, dport, dchan, protection):
        if dport not in self.switchxcdb: return None
        if dchan not in self.switchxcdb[dport]: return None
        if protection not in self.switchxcdb[dport][dchan]: return None
        return self.switchxcdb[dport][dchan][protection]

    def setupSwitchXC(self, sport, schan ,dport, dchan, xc):
        if dport not in self.switchxcdb: return None
        if dchan not in self.switchxcdb[dport]: self.switchxcdb[dport][dchan] = dict()
        if xc.protection not in self.switchxcdb[dport][dchan]:
            self.switchxcdb[dport][dchan][xc.protection] = (sport, schan, xc.rate, [xc])
        else:
            if xc not in self.switchxcdb[dport][dchan][xc.protection][3]:
                self.switchxcdb[dport][dchan][xc.protection][3].append(xc)
        self.regChannel(sport, schan, dport, dchan, xc.rate)

    def releaseSwitchXC(self, dport, dchan, xc):
        if xc.protection not in self.switchxcdb[dport][dchan]: return None
        sport, schan = self.switchxcdb[dport][dchan][xc.protection][0:2]
        self.unregChannel(sport, schan, dport, dchan)
        self.switchxcdb[dport][dchan][xc.protection][3].remove(xc)
        if not self.switchxcdb[dport][dchan][xc.protection][3]:
            del self.switchxcdb[dport][dchan][xc.protection]

    def regChannel(self, sport, schan, dport, dchan, rate):
        if schan in self.chandb[sport]: self.chandb[sport][schan].scnt += 1
        else: self.chandb[sport][schan] = Channel(1, 0, rate)
        if dchan in self.chandb[dport]: self.chandb[dport][dchan].dcnt += 1
        else: self.chandb[dport][dchan] = Channel(0, 1, rate)

    def unregChannel(self, sport, schan, dport, dchan):
        schannel = self.chandb[sport][schan]
        schannel.scnt -= 1
        if schannel.scnt == 0 and schannel.dcnt == 0: del self.chandb[sport][schan]
        dchannel = self.chandb[dport][dchan]
        dchannel.dcnt -= 1
        if dchannel.scnt == 0 and dchannel.dcnt == 0: del self.chandb[dport][dchan]

    def getChannelRate(self, port, chan):
        if chan in self.chandb[port]:
            return self.chandb[port][chan].rate
        else:
            return 0

    def getPortRate(self, port):
        rate = 0
        for chan in self.chandb[port]: rate += self.chandb[port][chan].rate
        return rate

class Card:
    def __init__(self, shelf, slot, switchdesc, switchlayout):
        self.shelf = shelf
        self.slot = slot
        self.porttype = dict()
        self.switches = self.buildSwitches(switchdesc)
        self.switchgraph = self.buildSwitchGraph(switchlayout)

    def buildSwitches(self, switchdesc):
        switches = list()
        for swd in switchdesc:
            switches.append(Switch(self, swd))
        return switches

    def buildSwitchGraph(self, switchlayout):
        switchgraph = MultiGraph()
        for layout in switchlayout:
            sswitch = layout[0]
            sport = int(layout[1][0])
            dswitch = layout[2]
            dport = int(layout[3][0])
            key = (sport << 16) + dport
            switchgraph.addEdge(sswitch, dswitch, key)
            self.porttype[sport] = layout[1][1]
            self.porttype[dport] = layout[3][1]
        return switchgraph

    def findSwitchPaths(self, sport, dport):
        ssw = list()
        dsw = list()
        paths = list()
        for switch in self.switches:
            if switch.hasPort(sport): ssw.append(self.switches.index(switch))
            if switch.hasPort(dport): dsw.append(self.switches.index(switch))
        for s in ssw:
            for d in dsw:
                paths += self.switchgraph.findPaths(s, d)
        return paths

    def findSwitchXCpath(self, sport, schan, dport, dchan, xc):
        #print 'findSwitchXCpath', sport, schan, dport, dchan, xc.protection, xc.rate
        switchpaths = self.findSwitchPaths(sport, dport);
        #print 'switch path', switchpaths
        switchpaths.sort(key=lambda x: len(x))
        switchxcpath = list()
        for switchpath in switchpaths:
            for pos in range(0, len(switchpath), 2):
                switch = self.switches[switchpath[pos]]
                if pos == (len(switchpath) - 1):
                    dport2 = dport
                    dchan2 = dchan
                else:
                    dport2 = int(switchpath[pos+1] >> 16)
                    dchan2 = None
                if dchan2:
                    swxc = switch.getSwitchXC(dport2, dchan2, xc.protection)
                    if swxc and swxc[0:2] != (sport, schan):
                        del switchxcpath[:]
                        break
                else:
                    dchan2 = switch.findChannel(sport, schan, dport2, xc)
                    if not dchan2:
                        del switchxcpath[:]
                        break
                switchxcpath.append(SwitchXC(self.shelf, self.slot, sport, schan, dport2, dchan2))
                if pos < (len(switchpath) - 1):
                    sport = (switchpath[pos+1] & 0xFFFF)
                    schan = dchan2
            if switchxcpath: break
        return switchxcpath

    def findSwitch(self, sport, dport):
        sswitches = list()
        dswitches = list()
        for switch in self.switches:
            if switch.hasPort(sport): sswitches.append(switch)
            if switch.hasPort(dport): dswitches.append(switch)
        switchfound = None
        for sswitch in sswitches:
            for dswitch in dswitches:
                if self.switches.index(sswitch) == self.switches.index(dswitch):
                    switchfound = sswitch
                    break
            if switchfound: break
        return switchfound

    def hasSwitchXC(self, sport, schan, dport, dchan):
        switch = self.findSwitch(sport, dport)
        if not switch: return False
        return switch.hasSwitchXC(sport, schan, dport, dchan)

    def setupSwitchXC(self, sport, schan, dport, dchan, xc):
        switch = self.findSwitch(sport, dport)
        if switch: switch.setupSwitchXC(sport, schan, dport, dchan, xc)

    def releaseSwitchXC(self, sport, schan, dport, dchan, xc):
        switch = self.findSwitch(sport, dport)
        if switch: switch.releaseSwitchXC(dport, dchan, xc)

    def setPortType(self, port, porttype):
        for switch in self.switches:
            if switch.getPortRate(port) > 0: return
        self.porttype[port] = porttype

    def getPortType(self, port):
        if port in self.porttype: return self.porttype[port]
        else: return None

class Shelf:
    def __init__(self, shelf, shelfdesc):
        self.desc = shelfdesc
        self.cards = dict()
        self.cards[2] = Card(shelf, 2, CARD_20P200_SWITCH, CARD_20P200_SWITCH_LAYOUT)
        self.cards[3] = Card(shelf, 3, CARD_20P200_SWITCH, CARD_20P200_SWITCH_LAYOUT)
        self.cards[4] = Card(shelf, 4, CARD_20P200_SWITCH, CARD_20P200_SWITCH_LAYOUT)
        self.cards[5] = Card(shelf, 5, CARD_20P200_SWITCH, CARD_20P200_SWITCH_LAYOUT)
        self.xcdb = list()

    def findSwitchXCPath(self, xc):
        switchxcpaths = self.findAllSwitchXCPaths(xc)
        minnewlength = 255
        minlength = 255
        bestswitchxcpath = None
        for switchxcpath in switchxcpaths:
            length = len(switchxcpath)
            newlength = self.getNewSwitchXCPathLength(switchxcpath)
            #print newlength, length
            if (newlength < minnewlength) or (newlength == minnewlength and \
                length  < minlength):
                bestswitchxcpath = switchxcpath
                minnewlength = newlength
                minlength = length
        return bestswitchxcpath

    def setupSwitchXCPath(self, xc, switchxcpath):
        for switchxc in switchxcpath:
            card = self.cards[switchxc.slot]
            card.setupSwitchXC(switchxc.sport, switchxc.schan, switchxc.dport, switchxc.dchan, xc)
        self.xcdb.append((xc, switchxcpath))

    def releaseSwitchXCPath(self, xc):
        for i in range(0,len(self.xcdb)):
            if self.xcdb[i][0] == xc:
                switchxcpath = self.xcdb[i][1]
                for switchxc in switchxcpath:
                    card = self.cards[switchxc.slot]
                    card.releaseSwitchXC(switchxc.sport, switchxc.schan, switchxc.dport, switchxc.dchan, xc)
                del self.xcdb[i]
                break

    def dumpSwitchXCPaths(self):
        for xc, switchxcpath in self.xcdb:
            print '========', xc, '========'
            for switchxc in switchxcpath:
                print switchxc

    def getNewSwitchXCPathLength(self, switchxcpath):
        length = 0
        for switchxc in switchxcpath:
            card = self.cards[switchxc.slot]
            if not card.hasSwitchXC(switchxc.sport, switchxc.schan, switchxc.dport, switchxc.dchan):
                length += 1
        return length

    def findAllSwitchXCPaths(self, xc):
        switchxcpaths = list()
        cardpaths = self.findCardPaths(xc.sslot, xc.dslot)
        #print 'cardpaths', cardpaths
        for cardpath in cardpaths:
            switchxcpath = self.findSwitchXCPathForCardPath(xc, cardpath)
            if switchxcpath: switchxcpaths.append(switchxcpath)
        return switchxcpaths

    def findSwitchXCPathForCardPath(self, xc, cardpath):
        #print 'cardpath', cardpath
        switchxcpath = list()
        sport = xc.sport
        schan = xc.schan
        for pos in range(0, len(cardpath), 2):
            card = self.cards[cardpath[pos]]
            if pos == (len(cardpath) - 1):
                dport = xc.dport
                dchan = xc.dchan
            else:
                dport = cardpath[pos+1]
                dchan = None
            cardswitchxcpath = card.findSwitchXCpath(sport, schan, dport, dchan, xc)
            if cardswitchxcpath:
                sport = cardswitchxcpath[-1].dport
                schan = cardswitchxcpath[-1].dchan
                switchxcpath += cardswitchxcpath
            else:
                return None
        return switchxcpath

    def findCardPaths(self, sslot, dslot):
        return self.buildCardGragh().findPaths(sslot, dslot)

    def buildCardGragh(self):
        connectors = list()
        for card in self.cards.itervalues():
            for switch in card.switches:
                for port in switch.ports:
                    if (port >= UP_CONNECTOR_N1):
                        connectors.append((card.slot, port))
        graph = MultiGraph()
        for i in range(len(connectors)):
            src = connectors[i]
            for j in range(i+1, len(connectors)):
                dst = connectors[j]
                if (src[0], src[1], dst[0], dst[1]) in self.desc or \
                   (dst[0], dst[1], src[0], src[1]) in self.desc:
                    graph.addEdge(src[0], dst[0], src[1]) 
        return graph
        
def testShelf():
    shelf = Shelf(1, PSS8_SHELF_BACKPLANE)

    xc1 = XC(1,2,1,1,1,5,15,1,False,10000);
    path1 = shelf.findSwitchXCPath(xc1);
    shelf.setupSwitchXCPath(xc1, path1)
    
    xc2 = XC(1,5,15,1,1,2,1,1,False,10000);
    path2 = shelf.findSwitchXCPath(xc2);
    shelf.setupSwitchXCPath(xc2, path2)

    xc3 = XC(1,2,1,2,1,5,15,2,False,10000);
    path3 = shelf.findSwitchXCPath(xc3);
    shelf.setupSwitchXCPath(xc3, path3)

    xc4 = XC(1,2,1,1,1,5,10,3,False,10000);
    path4 = shelf.findSwitchXCPath(xc4);
    shelf.setupSwitchXCPath(xc4, path4);

    xc5 = XC(1,2,1,1,1,4,20,3,True,10000);
    path5 = shelf.findSwitchXCPath(xc5);
    shelf.setupSwitchXCPath(xc5, path5);

    xc6 = XC(1,4,20,3,1,2,1,1,True,10000);
    path6 = shelf.findSwitchXCPath(xc6);
    shelf.setupSwitchXCPath(xc6, path6);

    shelf.dumpSwitchXCPaths()

    shelf.releaseSwitchXCPath(xc1)
    shelf.releaseSwitchXCPath(xc2)
    shelf.releaseSwitchXCPath(xc3)
    shelf.releaseSwitchXCPath(xc4)
    shelf.releaseSwitchXCPath(xc5)
    shelf.releaseSwitchXCPath(xc6)
    shelf.dumpSwitchXCPaths()

def testMultiGraph():
    graph = MultiGraph()
    graph.addEdge(2, 3, 1001)
    graph.addEdge(2, 3, 2001)
    graph.addEdge(2, 4, 1002)
    graph.addEdge(2, 4, 2002)
    graph.addEdge(2, 5, 1003)
    graph.addEdge(2, 5, 2003)
    graph.addEdge(3, 4, 1003)
    graph.addEdge(3, 4, 2003)
    graph.addEdge(3, 5, 1002)
    graph.addEdge(3, 5, 2002)
    graph.addEdge(4, 5, 1001)
    graph.addEdge(4, 5, 2001)
    print graph.getEdges()
    print graph.findPaths(2, 3)
    print graph.findPaths(2, 2)
    print graph.findPaths(2, 5)
    graph.removeEdge(2, 3, 1001)
    graph.removeEdge(2, 3, 2001)
    graph.removeEdge(2, 4, 1002)
    graph.removeEdge(2, 4, 2002)
    graph.removeEdge(2, 5, 1003)
    graph.removeEdge(2, 5, 2003)
    graph.removeEdge(3, 4, 1003)
    graph.removeEdge(3, 4, 2003)
    graph.removeEdge(3, 5, 1002)
    graph.removeEdge(3, 5, 2002)
    graph.removeEdge(4, 5, 1001)
    graph.removeEdge(4, 5, 2001)
    print graph.getEdges()


if __name__ == '__main__':
    #testMultiGraph()
    testShelf()
