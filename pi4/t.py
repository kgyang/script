#!bin/python3

from buildhat import PassiveMotor
from buildhat import Motor
from time import sleep

#m = Motor('A')
#m.run_for_seconds(seconds=10, speed=50)

#m = PassiveMotor('A')
#m.start(100)
#sleep(5)
#m.stop()

m = dict()
for n in ['A', 'B', 'C', 'D']:
    m[n] = PassiveMotor(n)
    m[n].start(-100)
sleep(5)

for n in m.keys():
    m[n].stop()

#for n in ['A', 'B']:
    #PassiveMotor(n).stop()

