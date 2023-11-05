#!/home/yf/bin/python3

from buildhat import PassiveMotor
from buildhat import Motor
from time import sleep

#m = Motor('A')
#m.run_for_seconds(seconds=50, speed=50)

#m = PassiveMotor('A')
#m.start(500)
#sleep(5)
#m.stop()

#m = dict()
#for n in ['A', 'B', 'C', 'D']:
    #m[n] = PassiveMotor(n)
    #m[n].start(50)
#sleep(5)
#
#for n in m.keys():
    #m[n].stop()

def right(rt):
    a = PassiveMotor('A')
    a.start(-50)

    b = PassiveMotor('B')
    b.start(-50)

    c = PassiveMotor('C')
    c.start(50)

    d = PassiveMotor('D')
    d.start(50)

    sleep(rt)
    a.stop()
    b.stop()
    c.stop()
    d.stop()

def left(rt):
    a = PassiveMotor('A')
    a.start(50)

    b = PassiveMotor('B')
    b.start(50)

    c = PassiveMotor('C')
    c.start(-50)

    d = PassiveMotor('D')
    d.start(-50)

    sleep(rt)
    a.stop()
    b.stop()
    c.stop()
    d.stop()

def clockwise(rt):
    a = PassiveMotor('A')
    a.start(-50)

    b = PassiveMotor('B')
    b.start(-50)

    c = PassiveMotor('C')
    c.start(-50)

    d = PassiveMotor('D')
    d.start(-50)

    sleep(rt)
    a.stop()
    b.stop()
    c.stop()
    d.stop()

def anticlockwise(rt):
    a = PassiveMotor('A')
    a.start(50)

    b = PassiveMotor('B')
    b.start(50)

    c = PassiveMotor('C')
    c.start(50)

    d = PassiveMotor('D')
    d.start(50)

    sleep(rt)
    a.stop()
    b.stop()
    c.stop()
    d.stop()

def backward(rt):
    a = PassiveMotor('A')
    a.start(-50)

    b = PassiveMotor('B')
    b.start(-50)

#    c = PassiveMotor('C')
 #   c.start(50)

  #  d = PassiveMotor('D')
   # d.start(50)

    sleep(rt)
    a.stop()
    b.stop()
#    c.stop()
 #   d.stop()

def ws(rt):
#    a = PassiveMotor('A')
 #   a.start(50)

    b = PassiveMotor('B')
    b.start(50)

    c = PassiveMotor('C')
    c.start(-50)

  #  d = PassiveMotor('D')
   # d.start(50)

    sleep(rt)
    #a.stop()
    b.stop()
    c.stop()
    #d.stop()






right(1)
left(1)
clockwise(1)
anticlockwise(1)
backward(1)
ws(1)
