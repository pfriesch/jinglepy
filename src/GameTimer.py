from datetime import datetime, timedelta
from queue import Queue
import config
from .PlayerThread import PlayerThread, QueuedJingle
from .helper import TournamentState, thread_sleep
from .helper import volume_control
from enum import Enum


class GameTimer:
    def __init__(self):

        self.clemVol = volume_control.volume_get()
        self.matchStartTime: datetime = datetime.fromtimestamp(0)
        self.matchEndTime: datetime = datetime.fromtimestamp(0)
        self.breakStartTime: datetime = datetime.fromtimestamp(0)
        self.breakEndTime: datetime = datetime.fromtimestamp(0)
        self.playerQueue: Queue[QueuedJingle] = Queue()
        self.ps = PlayerThread(self.playerQueue)
        self.ps.start()
        self.tournamentState = TournamentState.NotStarted

    def match_start(self):
        self.tournamentState = TournamentState.Match
        self.matchStartTime = datetime.now()
        self.matchEndTime = datetime.now() + config.gameLength

        self.playerQueue.put(QueuedJingle("gamesStarting",
                                          jingle_time=self.matchStartTime,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("halfTime",
                                          jingle_time=self.matchStartTime + config.halfTime,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("5minLeft",
                                          jingle_time=self.matchStartTime + config.gameLength - config.fiveMinLeft,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("1minLeft",
                                          jingle_time=self.matchStartTime + config.gameLength - config.oneMinLeft,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("gameOver",
                                          jingle_time=self.matchStartTime + config.gameLength,
                                          should_end_at_time=True,
                                          is_last_jingle=True))
        self.ps.jingleQueued.set()

    def break_start(self):
        self.tournamentState = TournamentState.Break
        self.breakStartTime: datetime = datetime.now()
        self.breakEndTime: datetime = datetime.now() + config.breakLength

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("5minToGame",
                                          jingle_time=self.breakStartTime + config.breakLength - config.fiveMinLeft,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

        # wait until queue is read
        while self.ps.jingleQueued.isSet():
            thread_sleep(0.1)
        # put match outro intro queue
        self.playerQueue.put(QueuedJingle("1minLeft",
                                          jingle_time=self.breakStartTime + config.breakLength - config.oneMinLeft,
                                          should_end_at_time=True,
                                          is_last_jingle=False))
        self.ps.jingleQueued.set()

    @staticmethod
    def time_str(t: datetime):
        return t.strftime("%H:%M:%S")
