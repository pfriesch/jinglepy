import time
import datetime
from queue import Queue
import config
from .PlayerThread import PlayerThread
from .helper import formated_time
from .NativeVoolumeControls import NativeVolumeControls
from enum import Enum


class TournamentState(Enum):
    NotStarted = "NotStarted"
    Match = "Match"
    Break = "Break"


class GameTimer:
    def __init__(self):
        self.matchLength = config.gameLength  # * 60
        self.breakLength = config.breakLength  # * 60
        self.nMinutes = config.nLastMinutes  # * 60
        self.clemVol = NativeVolumeControls.volume_get()
        self.matchStartTime = 0
        self.matchEndTime = 0
        self.breakStartTime = 0
        self.breakEndTime = 0
        self.playerQueue = Queue()
        self.ps = PlayerThread(self.playerQueue)
        self.ps.start()
        self.tournamentState = TournamentState.NotStarted

    def match_start(self):
        self.tournamentState = TournamentState.Match
        self.matchStartTime = int(time.time()) + 1
        self.matchEndTime = self.matchStartTime + self.matchLength
        self.nMinutesTime = self.matchEndTime - self.nMinutes
        #       queue format  [  jingle , time , True if time = time when jingle should end , True if segment ends after jingle ]
        self.playerQueue.put(["gamesStarting", self.nMinutesTime, False, False])
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            time.sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(["1minLeft", self.matchEndTime, True, True])
        self.ps.jingleQueued.set()

    def break_start(self):
        self.tournamentState = TournamentState.Break
        self.breakStartTime = int(time.time())
        self.breakEndTime = self.breakStartTime + self.breakLength
        self.playerQueue.put(["halfTime", self.breakEndTime, True, True])
        self.ps.jingleQueued.set()

    def match_time_start_str(self):
        return formated_time(self.matchStartTime)

    def match_time_end_str(self):
        return formated_time(self.matchEndTime)

    @staticmethod
    def time_str(t):
        return formated_time(t)

    @staticmethod
    def time_remaining(t):
        secs = abs(int(t - time.time()))
        if secs > 3600:
            secs = 0
        return str(datetime.timedelta(seconds=int(secs)))
