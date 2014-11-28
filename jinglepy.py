import dbus
import subprocess
import threading
import time
from curses import wrapper
import config

c = config

#init Dbus interface
session_bus = dbus.SessionBus()

try:
    player = session_bus.get_object('org.mpris.clementine' , '/Player')
except:
    #launch clementine if needed
    clem = subprocess.Popen('clementine' , stdout=subprocess.PIPE , stderr=subprocess.PIPE)
    time.sleep(2)
    player = session_bus.get_object('org.mpris.clementine' , '/Player')

iface = dbus.Interface(player,dbus_interface='org.freedesktop.MediaPlayer')

class GameTimer():
    def __init__(self):
        self.gameLength = c.gameLength*60
        self.breakLength = c.breakLength*60
        self.breakJingle = c.breakJingle
        self.sixtySecondsJingle = c.sixtySecondsJingle
        self.clemVol = iface.VolumeGet()

    #mplayer subprocess prototype
    def mPlayer(self, audiofile):
        self.mplayer = subprocess.Popen(["mplayer" , "-quiet" , audiofile ] , stdout=subprocess.PIPE , stderr=subprocess.PIPE ) 
        self.mplayer.wait()
    
    def clemChangeVol(self,startVol,endVol):
        diff = startVol - endVol
        steps = 20
        step = diff/steps
        curVol = startVol
        for i in range(steps) :
            curVol = curVol - step
            iface.VolumeSet(curVol)
            time.sleep(.1)

    def playSixty(self):
        self.clemVol = iface.VolumeGet()
        self.clemChangeVol(self.clemVol,0)
        self.mPlayer(self.sixtySecondsJingle)
        time.sleep(5)
        self.clemChangeVol(0,self.clemVol)

    def matchStart(self):
        self.MatchStartTime=time.time()
        self.matchThread = threading.Timer(self.gameLength-60 , self.playSixty)
        self.matchThread.start()



def main(stdscr):
    
    #init GameTimer
    gt=GameTimer()
    
    stdscr.clear()
    while True :
        stdscr.refresh()
        k=stdscr.getkey()
        
        options = { "P" : iface.Play ,
                    "S" : iface.Stop ,
                    "s" : gt.matchStart ,
                    "p" : gt.playSixty
                }

        options[k]()

#        try:
#            options[k]()
#        except:
#            print("something went wrong")

        time.sleep(1)


#init curses
wrapper(main)

