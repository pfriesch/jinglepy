import dbus
import subprocess
import threading
import time
import curses, curses.panel
import config
import sys
import select

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



class Ui:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)

        self.win1 = curses.newwin(30,20,0,0)
        self.win1.border(0)
        self.win2 = curses.newwin(30,20,0,22)
        self.win2.border(0)
        
        self.win1.addstr(1,1,"win1")
        self.win2.addstr(1,1,"win2")

    def refresh (self):
        self.win1.refresh()
        self.win2.refresh()

    def quitUi(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()
        exit(0)

class Feeder:
    def __init__(self):
        self.running = False
        self.ui = Ui()
        self.gt = GameTimer()
        self.count = 0
        self.key = "i"
    
    def run(self):
        self.running = True
        self.feed()

    def stop (self):
        self.ui.quitUi()
        self.running = False

    def feed(self):
        while self.running :
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                self.key = sys.stdin.read(1)
                options = { "p" : self.gt.playSixty ,
                        "P" : iface.Play ,
                        "q" : self.stop ,
                        "s" : self.gt.matchStart ,
                        "S" : iface.Stop 
                        }
                try:
                    options[self.key]()
                except:
                    self.ui.win2.addstr(2,1,"Command is unknown or failed.")
        
            self.ui.win1.addstr(2,1,"Count is:" + str(self.count))
            self.ui.win1.addstr(3,1,"Last input:" + self.key)
            self.ui.refresh()
            time.sleep(0.1)
            self.count += 1



#init curses
#wrapper(main)
if __name__ == "__main__":
    f = Feeder()
    f.run()
