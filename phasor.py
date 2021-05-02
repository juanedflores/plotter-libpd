import pyaudio
from pylibpd import *
import time
import re
import threading

f = open('test.gcode', 'r')

p = pyaudio.PyAudio()

ch = 1
sr = 44100
tpb = 6
bs = libpd_blocksize()

stream = p.open(format=pyaudio.paInt16,
                channels=ch,
                rate=sr,
                input=True,
                output=True,
                frames_per_buffer=bs * tpb)

m = PdManager(ch, ch, sr, 1)
libpd_open_patch('funtest.pd')


def updatexy(x, y):
    print("UPDATING..")
    libpd_float('x', float(x)-40)
    libpd_float('y', float(y))
    libpd_bang('trigger')


def plotter_lines():
    XLocation = 0
    YLocation = 0
    for line in f:
        l = line.strip()
        time.sleep(0.4)
        print('Sending ' + l)
        Xsearch = re.search(r"X(\d+\.\d+)", l)
        Ysearch = re.search(r"Y(\d+\.\d+)", l)
        print(Xsearch)
        if (Xsearch != None):
            XLocation = Xsearch.groups()[0]
            YLocation = Ysearch.groups()[0]
            print("XL: " + str(XLocation) + " YL: " + str(YLocation))

            updatexy(XLocation, YLocation)


x = threading.Thread(target=plotter_lines)
x.start()

while 1:
    data = stream.read(bs)
    outp = m.process(data)
    stream.write(bytes(outp))


f.close()
stream.close()
p.terminate()
libpd_release()
