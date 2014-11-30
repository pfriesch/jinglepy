import dbus
import subprocess
import threading
import time , datetime
import curses, curses.panel
import config
import sys
import select
import objgraph


from gi.repository import Gst

Gst.init(sys.argv)

c = config

def og():
    objgraph.show_refs([f])


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


class GameTimer():
    def __init__(self):
        self.gameLength = c.gameLength*60
        self.breakLength = c.breakLength*60
        self.clemVol = iface.VolumeGet()
        self.matchStartTime = 0
        self.matchEndTime = 0
        self.breakStartTime = 0
        self.breakEndTime = 0
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

    def playJingle(self,j,fadeout=True,fadein=True):
        jingle = self.jingles[j]
        curClemVol = iface.VolumeGet()
        if curClemVol != 0 & fadeout :
            self.clemVol == curClemVol
            self.clemChangeVol(self.clemVol,0)
        jingle.stop()
        jingle.play()
        time.sleep( jingle.duration )
        if fadein :
            self.clemChangeVol(0,self.clemVol)
        return 0

    def matchStart(self):
        matchStartThread = threading.Timer( 0 , self.playJingle , args = ("matchStart" ) )
        matchStartThread.start()
        self.matchStartTime = time.time()
        self.matchEndTime = self.matchStartTime + self.gameLength
        matchEndThread = threading.Timer( self.gameLength - self.jingles["matchStart"].duration - 1 , self.playJingle , args = ("matchStart") )
        matchEndThread.start()

    def breakStart(self):
        self.breakStartTime = time.time()
        self.breakEndTime = breakStartTime + self.breakLength
        breakEndThread = threading.Timer( self.breakLength - self.jingles["breakEnd"].duration - 1 , self.playJingle , args = ( "breakEnd" ) )

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
        self.count = 0
        self.key = "i"
    
    def run(self):
        self.running = True
        self.feed()

    def stop (self):
        self.running = False
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
                        "s" : self.gt.matchStart ,
                        "S" : iface.Stop 

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


            self.ui.win1.addstr(2,1,"Count is:" + str(self.count))
            self.ui.win1.addstr(3,1,"Last input:" + self.key)
            self.ui.win1.addstr(4,1,"Threads:" + str(threading.enumerate()))


            self.ui.win2.addstr(2,1,"Match started  @ " + self.gt.TimeStr( self.gt.matchStartTime ) )
            self.ui.win2.addstr(3,1,"Match ends     @ " + self.gt.TimeStr( self.gt.matchEndTime ) ) 
            self.ui.win2.addstr(4,1,"Remaining Time :  " + self.gt.TimeRemaining( self.gt.matchEndTime ) )

            self.ui.win3.addstr(2,1,"Break started  @ " + self.gt.TimeStr( self.gt.breakStartTime ) ) 
            self.ui.win3.addstr(3,1,"Break ends     @ " + self.gt.TimeStr( self.gt.breakEndTime) ) 
            self.ui.win3.addstr(4,1,"Remaining Time :  " + self.gt.TimeRemaining(  self.gt.breakEndTime ) )

            self.ui.refresh()
            self.count += 1
            time.sleep(0.1)


if __name__ == "__main__":

    f = Feeder()
    f.run()
