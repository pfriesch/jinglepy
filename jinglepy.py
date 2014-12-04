import dbus
import subprocess
import threading
import time , datetime
import curses, curses.panel
import config
import sys
import select
import objgraph
from queue import Queue

from gi.repository import Gst

Gst.init(sys.argv)

c = config

def og():
    objgraph.show_refs([f])

q = Queue

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

class Jingles():
    def __init__(self,audiofile):
        self.player = Gst.ElementFactory.make("playbin","player")
        self.player.set_property("uri",audiofile)
        self.player.set_state(Gst.State.PLAYING)
        time.sleep(0.1)
        self.duration=round (self.player.query_duration(Gst.Format.TIME)[1] / Gst.SECOND , 1)
        self.player.set_state(Gst.State.NULL)
    
    def play(self):
        self.player.set_state(Gst.State.PLAYING)

    def pause(self):
        self.player.set_state(Gst.State.PAUSE)

    def stop(self):
        self.player.set_state(Gst.State.NULL)


class Ui:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)

        self.sss = self.stdscr.getmaxyx()

        self.win1 = curses.newwin(self.sss[0] - 10, self.sss[1] - 30, 0, 0)
        self.win2 = curses.newwin(self.sss[0] - 10, 30, 0, self.sss[1] - 30)
        self.pan2 = curses.panel.new_panel(self.win2)
        self.win3 = curses.newwin(self.sss[0] - 10, 30, 0, self.sss[1] - 30)
        self.pan3 = curses.panel.new_panel(self.win3)
        
        self.pan2.hide()

    def refresh (self):
        curses.panel.update_panels()
        self.win1.refresh()
        self.win2.refresh()
        self.win3.refresh()

    def switch_pan(self):

        def switch(fromPanel, toPanel):
            fromPanel.bottom()
            fromPanel.hide()
            toPanel.top()
            toPanel.show()

        if self.pan2.hidden():
            switch(self.pan3, self.pan2)
        else:
            switch(self.pan2, self.pan3)

        self.refresh()

    def quitUi(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()
        exit(0)


class playerThread(threading.Thread) :
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.tournamentInProgress = threading.Event()
        self.jingleQueued = threading.Event()
        self.terminate = threading.Event()
        self.fadeIn = threading.Event()
        self.jingleReady = threading.Event()
        self.lastJingle = threading.Event()
        self.segmentDone = threading.Event()
        self.queue = queue
        self.clemVol = iface.VolumeGet()
        self.jingleEnd = 0
        self.jingleStart = 0
        self.queuedJingle = ""

        self.jingles={}
        for name in c.jingles:
            jingle = Jingles( c.jingles[name])
            self.jingles[name] = jingle

    def clemChangeVol(self,startVol,endVol):
        diff = startVol - endVol
        steps = 20
        step = diff/steps
        curVol = startVol
        for i in range(steps) :
            curVol = curVol - step
            iface.VolumeSet(curVol)
            time.sleep(.05)

    def playJingle(self, j, fadeout = True, fadein = True ):
        jingle = self.jingles[j]
        if fadein:
            self.fadeIn.set()
        curClemVol = iface.VolumeGet()
        if curClemVol != 0 & fadeout :
            self.clemVol = curClemVol
            self.clemChangeVol(curClemVol, 0 )
        jingle.stop()
        jingle.play()
        return jingle

    def run (self):
        while True :
            while self.tournamentInProgress.isSet() :
                if self.jingleQueued.isSet() :
                    q = self.queue.get()
                    self.queuedJingle = q[0]
                    self.jingleEnd = q[1]
                    self.jingleStart = round (self.jingleEnd - self.jingles[self.queuedJingle].duration,0)
                    self.jingleReady.set()
                    self.jingleQueued.clear()

                elif self.jingleStart == round (time.time()) | self.jingleReady.isSet():  
                    jingle = self.playJingle(self.queuedJingle)
                    self.jingleEnd = round( time.time() + jingle.duration , 0)
                    self.jingleReady.clear()

                elif self.jingleEnd == round (time.time()) | self.fadeIn.isSet() :
                    self.clemChangeVol(0, self.clemVol)
                    self.fadeIn.clear()
                    if self.lastJingle.isSet() :
                        self.segmentDone.set()



                elif self.terminate.isSet() :
                    try:
                        jingle.stop()
                    except:
                        pass
                    return 0
                time.sleep(1)

def test():
    tq=Queue()
    tq.put(['sixtySecond', int(time.time()+10) ])
    pt=playerThread(tq)
    pt.start()
    pt.tournamentInProgress.set()
    pt.jingleQueued.set()
    return [pt,tq]

class GameTimer():
    def __init__(self):
        self.gameLength = c.gameLength*60
        self.breakLength = c.breakLength*60
        self.clemVol = iface.VolumeGet()
        self.matchStartTime = 0
        self.matchEndTime = 0
        self.breakStartTime = 0
        self.breakEndTime = 0
        self.playerQueue = Queue()
        self.ps = playerThread(self.playerQueue)
        self.ps.start()

    def matchStart(self):
        matchStartThread = threading.Timer( 0 , self.playJingle , args = ("matchStart" ) )
        matchStartThread.start()
        self.matchStartTime = time.time()
        self.matchEndTime = self.matchStartTime + self.gameLength
        matchEndThread = threading.Timer( self.gameLength - self.jingles["matchStart"].duration - 1 , self.playJingle , args = ("matchStart") )
        matchEndThread.start()

    def breakStart(self):
        self.breakStartTime = int(time.time())
        self.breakEndTime = self.breakStartTime + self.breakLength
        self.playerQueue.put( ["nMinutesJingle" , self.breakEndTime ] )
        self.ps.lastJingle.set()
        self.ps.jingleQueued.set()

    def startTournament(self):
        self.ps.tournamentInProgress.set()
        self.breakStart()

    def matchTimeStartStr(self):
        return time.strftime("%H:%M:%S" , time.localtime( self.matchStartTime ) )

    def matchTimeEndStr(self):
        return time.strftime("%H:%M:%S" , time.localtime( self.matchEndTime ) )

    def TimeStr(self, t):
        return time.strftime("%H:%M:%S" , time.localtime( t ) )

    def TimeRemaining(self, t):
        secs = abs( int( t - time.time() ) )
        if secs > 3600 : secs = 0
        return str( datetime.timedelta( seconds=int( secs ) ) )


class Feeder:
    def __init__(self):
        self.running = False
        self.ui = Ui()
        self.gt = GameTimer()
        self.segment = ""
        self.count = 0
        self.key = "i"
    
    def run(self):
        self.running = True
        self.feed()

    def startTournament(self):
        self.segment = "break"
        self.gt.startTournament ()

    def stop (self):
        self.running = False
        self.gt.ps.terminate.set()
        self.ui.quitUi()

    def feed(self):
        while self.running :
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                self.key = sys.stdin.read(1)
                options = {
                        "l" : self.ui.switch_pan , 
                        "M" : og,
                        "P" : iface.Play ,
                        "q" : self.stop ,
                        "s" : self.gt.breakStart ,
                        "S" : iface.Stop ,
                        "t" : self.startTournament

                        }
#                try:
                options[self.key]()
#                except:
#                    self.ui.win1.addstr(10,1,"Command is unknown or failed." +str( sys.exc_info()[0]) )

            if self.count%1000 == 0:
                self.ui.win1.clear()
                self.ui.win2.clear()
                self.ui.win3.clear()

                self.ui.win1.border(0)
                self.ui.win2.border(0)
                self.ui.win3.border(0)

                self.ui.win1.addstr(1,1,"win1")
                self.ui.win2.addstr(1,1,"Match:")
                self.ui.win3.addstr(1,1,"Break:")


            self.ui.win1.addstr(2,1,"Count is: " + str(self.count) )
            self.ui.win1.addstr(3,1,"Last input: " + self.key)
            self.ui.win1.addstr(4,1,"Turnament State: " + str( self.gt.ps.jingleStart ) )
            self.ui.win1.addstr(5,1,"Threads:" + str(threading.enumerate() ) )


            self.ui.win2.addstr(2,1,"Match started  @ " + self.gt.TimeStr( self.gt.matchStartTime ) )
            self.ui.win2.addstr(3,1,"Match ends     @ " + self.gt.TimeStr( self.gt.matchEndTime ) ) 
            self.ui.win2.addstr(4,1,"Remaining Time :  " + self.gt.TimeRemaining( self.gt.matchEndTime ) )

            self.ui.win3.addstr(2,1,"Break started  @ " + self.gt.TimeStr( self.gt.breakStartTime ) ) 
            self.ui.win3.addstr(3,1,"Break ends     @ " + self.gt.TimeStr( self.gt.breakEndTime) ) 
            self.ui.win3.addstr(4,1,"Remaining Time :  " + self.gt.TimeRemaining(  self.gt.breakEndTime ) )

            self.ui.refresh()
            self.count += 1

            if self.gt.ps.segmentDone.isSet() :
                self.gt.ps.segmentDone.clear()
                if self.segment == "break" :
                    self.segment = "match"
                    self.gt.matchStart()

                elif self.segment == "match":
                    self.segment = "break"
                    self.gt.breakStart()



            time.sleep(0.1)


if __name__ == "__main__":

    f = Feeder()
    f.run()
