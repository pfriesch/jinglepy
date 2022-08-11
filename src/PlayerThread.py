import threading
from dataclasses import dataclass
from datetime import datetime
from queue import Queue

from .Jingles import Jingles
from .helper import volume_control, thread_sleep
import config


@dataclass
class QueuedJingle:
    jingle_id: str
    jingle_time: datetime
    should_end_at_time: bool
    is_last_jingle: bool


class PlayerThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.tournamentInProgress = threading.Event()
        self.jingleQueued = threading.Event()
        self.terminate = threading.Event()
        self.fadeIn = threading.Event()
        self.jingleReady = threading.Event()
        self.lastJingle = threading.Event()
        self.segmentDone = threading.Event()
        self.queue: Queue[QueuedJingle] = queue
        self.clemVol = volume_control.volume_get()
        self.jingleEnd: datetime = datetime.fromtimestamp(0)
        self.jingleStart: datetime = datetime.fromtimestamp(0)
        self.jingleQueue = {}
        self.queuedJingle = ""

        self.jingles = {}
        for name in config.jingles:
            jingle = Jingles(config.jingles[name])
            self.jingles[name] = jingle

    @classmethod
    def clem_change_vol(cls, start_vol, end_vol):
        diff = start_vol - end_vol
        steps = 20
        step = diff / steps
        cur_vol = start_vol
        for i in range(steps):
            cur_vol = cur_vol - step
            volume_control.volume_set(cur_vol)
            thread_sleep(.05)

    def play_jingle(self, j, fadeout=True, fadein=True):
        jingle = self.jingles[j]
        if fadein:
            self.fadeIn.set()
        cur_clem_vol = volume_control.volume_get()
        if cur_clem_vol != 0 & fadeout:
            self.clemVol = cur_clem_vol
            PlayerThread.clem_change_vol(cur_clem_vol, 0)
        jingle.stop()
        jingle.play()
        return jingle

    def run(self):
        while True:
            while self.tournamentInProgress.isSet():
                if self.jingleQueued.isSet():
                    next_jingle = self.queue.get()
                    jingle_id = next_jingle.jingle_id
                    if next_jingle.should_end_at_time:
                        jingle_end = next_jingle.jingle_time
                        jingle_start = jingle_end - self.jingles[jingle_id].get_duration()
                    else:
                        jingle_start = next_jingle.jingle_time
                    is_last_jingle = next_jingle.is_last_jingle
                    self.jingleQueue[jingle_start] = [jingle_id, is_last_jingle]
                    self.jingleQueued.clear()

                for jingle_time in self.jingleQueue.keys():
                    if jingle_time >= datetime.now():
                        j = self.jingleQueue.pop(jingle_time)
                        jingle = self.play_jingle(j[0])
                        print("playing jingle")
                        if j[1]:
                            self.lastJingle.set()
                        self.jingleEnd = datetime.now() + jingle.get_duration()
                        break

                if self.jingleEnd >= datetime.now():  # | self.fadeIn.isSet() :
                    self.clem_change_vol(0, self.clemVol)
                    self.fadeIn.clear()
                    if self.lastJingle.isSet():
                        self.segmentDone.set()
                        self.lastJingle.clear()

                if self.terminate.isSet():
                    try:
                        jingle.stop()
                    except:
                        pass
                    return 0
                thread_sleep(0.1)
            thread_sleep(0.1)
