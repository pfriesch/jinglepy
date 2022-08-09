import time
import config
import sys
import select

from .GameTimer import GameTimer, TournamentState
from .NativeVoolumeControls import NativeVolumeControls
from .Ui import Ui
from .helper import formated_time
from enum import Enum


class Feeder:
    def __init__(self):
        self.running = False
        self.ui = Ui()
        self.gt = GameTimer()
        self.segment: TournamentState = TournamentState.NotStarted
        self.count = 0
        self.key = "i"
        self.tournamentStartTime = int(time.mktime(time.strptime(config.tournamentStartTime, "%d.%m.%y %H:%M:%S")))
        self.wheel = ["|", '/', "-", "\\"]

    def run(self):
        self.running = True
        self.feed()

    def start_tournament(self):
        self.segment = TournamentState.Break
        self.ui.swpan(self.ui.match_panel, self.ui.break_panel)
        self.gt.ps.tournamentInProgress.set()
        self.gt.break_start()

    def stop(self):
        self.running = False
        self.gt.ps.terminate.set()
        self.ui.quit_ui()

    def feed(self):
        while self.running:
            while sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
                try:
                    self.key = sys.stdin.read(1)
                except:
                    print("")
                options = {
                    "l": self.ui.switch_pan,
                    "P": NativeVolumeControls.play,
                    "q": self.stop,
                    "s": self.gt.break_start,
                    "S": NativeVolumeControls.stop,
                    "t": self.start_tournament
                }
                try:
                    options[self.key]()
                except:
                    self.ui.main_window.addstr(10, 1, "Command is unknown or failed." + str(sys.exc_info()[0]))

            if self.count % 100 == 0:
                self.ui.main_window.clear()
                self.ui.match_window.clear()
                self.ui.break_window.clear()

                self.ui.main_window.border(0)
                self.ui.match_window.border(0)
                self.ui.break_window.border(0)

                self.ui.main_window.addstr(1, 1, "JingleQueue:")
                self.ui.match_window.addstr(1, 1, "Match:")
                self.ui.break_window.addstr(1, 1, "Break:")

                self.ui.main_window.addstr(13, 1, "Keycommands:")
                self.ui.main_window.addstr(14, 2, "[S]top music playback")
                self.ui.main_window.addstr(15, 2, "Start music [P]layback")
                self.ui.main_window.addstr(16, 2, "Tog[l]le interface")
                self.ui.main_window.addstr(17, 2, "S[t]art tournament")
                self.ui.main_window.addstr(18, 2, "[q]uit jinglepy")

            self.ui.main_window.addstr(2, 1, "Alive: " + str(self.wheel[self.count % 4]))
            self.ui.main_window.addstr(2, 20, "time: " + str(formated_time(time.time())))
            self.ui.main_window.addstr(3, 1, "tournament starts @:     " + str(formated_time(self.tournamentStartTime)))
            self.ui.main_window.addstr(4, 1, "Last input: " + self.key)
            self.ui.main_window.addstr(5, 1, "Tournament State: " + str(self.gt.tournamentState))
            self.ui.main_window.addstr(6, 1, "Queued jingles: ")

            queueline = 6
            nextfreeline = 1
            for k in self.gt.ps.jingleQueue:
                line = queueline + nextfreeline
                self.ui.main_window.addstr(line, 2, formated_time(k) + " " + str(self.gt.ps.jingleQueue[k][0]))
                nextfreeline += 1

            self.ui.match_window.addstr(2, 1, "Match started  @ " + self.gt.time_str(self.gt.matchStartTime))
            self.ui.match_window.addstr(3, 1, "Match ends     @ " + self.gt.time_str(self.gt.matchEndTime))
            self.ui.match_window.addstr(4, 1, "Remaining Time :  " + self.gt.time_remaining(self.gt.matchEndTime))

            self.ui.break_window.addstr(2, 1, "Break started  @ " + self.gt.time_str(self.gt.breakStartTime))
            self.ui.break_window.addstr(3, 1, "Break ends     @ " + self.gt.time_str(self.gt.breakEndTime))
            self.ui.break_window.addstr(4, 1, "Remaining Time :  " + self.gt.time_remaining(self.gt.breakEndTime))

            self.ui.refresh()
            self.count += 1

            if self.gt.ps.segmentDone.isSet():
                self.gt.ps.segmentDone.clear()
                if self.segment == TournamentState.Break:
                    self.segment = TournamentState.Match
                    self.ui.swpan(self.ui.break_panel, self.ui.match_panel)
                    self.gt.match_start()

                elif self.segment == TournamentState.Match:
                    self.segment = TournamentState.Break
                    self.ui.swpan(self.ui.match_panel, self.ui.break_panel)
                    self.gt.break_start()

            # check if it is time to start the tournament
            if self.gt.tournamentState == TournamentState.NotStarted:
                if self.tournamentStartTime - self.gt.breakLength == int(time.time()):
                    self.start_tournament()

            time.sleep(0.1)
