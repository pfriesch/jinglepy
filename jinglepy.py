import dbus
import subprocess
import threading
import time , datetime
import curses, curses.panel
import config
import sys
import select
import objgraph
import vlc
from queue import Queue


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
    time.sleep(5)
    player = session_bus.get_object('org.mpris.clementine' , '/Player')

iface = dbus.Interface(player,dbus_interface='org.freedesktop.MediaPlayer')

class Jingles():
    def __init__(self,audiofile):
        self.player = vlc.MediaPlayer(audiofile)
        self.player.play()
        time.sleep(0.1)
        self.duration= round(self.player.get_length() / 1000 , 1)
        self.player.stop()
    
    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()


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

    def swpan(self , fromPanel , toPanel) :

        fromPanel.bottom()
        fromPanel.hide()
        toPanel.top()
        toPanel.show()

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
        self.jingleQueue = {}
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
                    qJingle = q[0]
                    if q[2] :
                        jingleEnd = q[1]
                        jingleStart = round (jingleEnd - self.jingles[qJingle].duration - 1 ,0 )
                    else :
                        jingleStart = q[1]
                    lastJingle = q[3]
                    self.jingleQueue[jingleStart]=[qJingle,lastJingle]
                    self.jingleQueued.clear()

                for t in self.jingleQueue.keys() :
                    if t == round( time.time()) :
                        j = self.jingleQueue.pop(t)
                        jingle = self.playJingle( j[0] )
                        if j[1] :
                            self.lastJingle.set()
                        self.jingleEnd = round( time.time() + jingle.duration , 0)
                        break

                if self.jingleEnd == round (time.time()) : #| self.fadeIn.isSet() :
                    self.clemChangeVol(0, self.clemVol)
                    self.fadeIn.clear()
                    if self.lastJingle.isSet() :
                        self.segmentDone.set()
                        self.lastJingle.clear()

                if self.terminate.isSet() :
                    try:
                        jingle.stop()
                    except:
                        pass
                    return 0
                time.sleep(0.1)
            time.sleep(0.1)


class GameTimer():
    def __init__(self):
        self.matchLength = c.gameLength*60
        self.breakLength = c.breakLength*60
        self.nMinutes = c.nLastMinutes*60
        self.clemVol = iface.VolumeGet()
        self.matchStartTime = 0
        self.matchEndTime = 0
        self.breakStartTime = 0
        self.breakEndTime = 0
        self.playerQueue = Queue()
        self.ps = playerThread(self.playerQueue)
        self.ps.start()
        self.tournamentState = "Not started"

    def matchStart(self):
        self.tournamentState = "Match"
        self.matchStartTime = int(time.time()) + 1
        self.matchEndTime = self.matchStartTime + self.matchLength
        self.nMinutesTime = self.matchEndTime - self.nMinutes
#       queue format  [  jingle , time , True if time = time when jingle should end , True if segment ends after jingle ]      
        self.playerQueue.put( ["nMinutes", self.nMinutesTime , False , False ] )
        self.ps.jingleQueued.set()
        
        #wait until queue is read
        while self.ps.jingleQueued.isSet() :
            time.sleep(0.1)
        #put match outro intro queue
        self.playerQueue.put( ["sixtySecond" , self.matchEndTime , True , True ] )
        self.ps.jingleQueued.set()

    def breakStart(self):
        self.tournamentState = "Break"
        self.breakStartTime = int(time.time())
        self.breakEndTime = self.breakStartTime + self.breakLength
        self.playerQueue.put( ["breakEnd" , self.breakEndTime , True , True ] )
        self.ps.jingleQueued.set()

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
        self.tournamentStartTime = int( time.mktime( time.strptime( c.tournamentStartTime , "%d.%m.%y %H:%M:%S" ) ) )

    def run(self):
        self.running = True
        self.feed()

    def startTournament(self):
        self.segment = "break"
        self.ui.swpan(self.ui.pan3, self.ui.pan2)
        self.gt.ps.tournamentInProgress.set()
        self.gt.breakStart()

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
                try:
                    options[self.key]()
                except:
                    self.ui.win1.addstr(10,1,"Command is unknown or failed." +str( sys.exc_info()[0]) )

            if self.count%100 == 0:
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
            self.ui.win1.addstr(2,20, "time: "  + str (int(time.time())))
            self.ui.win1.addstr(3,1, "tournament starts @:     "  + str (self.tournamentStartTime))
            self.ui.win1.addstr(4,1,"Last input: " + self.key)
            self.ui.win1.addstr(5,1,"Tournament State: " + self.gt.tournamentState )
            self.ui.win1.addstr(6,1,"Queued jingles" + str( self.gt.ps.jingleQueue ) )


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
                    self.ui.swpan(self.ui.pan2, self.ui.pan3)
                    self.gt.matchStart()

                elif self.segment == "match":
                    self.segment = "break"
                    self.ui.swpan(self.ui.pan3, self.ui.pan2)
                    self.gt.breakStart()

            #check if it is time to start the tournament
            if self.gt.tournamentState == "Not started" :
                if self.tournamentStartTime - self.gt.breakLength == int(time.time()) :
                    self.startTournament()

            time.sleep(0.1)


if __name__ == "__main__":

    f = Feeder()
    f.run()
