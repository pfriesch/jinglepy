import threading
import time
from dataclasses import dataclass
from queue import Queue

from .Jingles import Jingles
import config
from .NativeVoolumeControls import NativeVolumeControls


@dataclass
class QueuedJingle:
    jingle_id: str
    jingle_time: int
    should_end_at_time: bool
    last_jingle: bool


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
        self.clemVol = NativeVolumeControls.volume_get()
        self.jingleEnd = 0
        self.jingleStart = 0
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
            NativeVolumeControls.volume_set(cur_vol)
            time.sleep(.05)

    def play_jingle(self, j, fadeout=True, fadein=True):
        jingle = self.jingles[j]
        if fadein:
            self.fadeIn.set()
        cur_clem_vol = NativeVolumeControls.volume_get()
        if cur_clem_vol != 0 & fadeout:
            self.clemVol = cur_clem_vol
            PlayerThread.clem_change_vol(cur_clem_vol, 0)
        jingle.stop()
        jingle.play()
        return jingle

    def run(self):
        jingle = self.play_jingle("gamesStarting")

        time.sleep(5000)

        while True:
            while self.tournamentInProgress.isSet():
                if self.jingleQueued.isSet():
                    nextJingle = self.queue.get()
                    jingle_id = nextJingle.jingle_id
                    if nextJingle.should_end_at_time:
                        jingle_end = nextJingle.jingle_time
                        jingle_start = round(jingle_end - self.jingles[jingle_id].get_duration() - 1, 0)
                    else:
                        jingle_start = nextJingle.jingle_time
                    last_jingle = nextJingle.last_jingle
                    self.jingleQueue[jingle_start] = [jingle_id, last_jingle]
                    self.jingleQueued.clear()

                for t in self.jingleQueue.keys():
                    if t <= round(time.time()):
                        j = self.jingleQueue.pop(t)
                        jingle = self.play_jingle(j[0])
                        if j[1]:
                            self.lastJingle.set()
                        self.jingleEnd = round(time.time() + jingle.get_duration(), 0)
                        break

                if self.jingleEnd <= round(time.time()):  # | self.fadeIn.isSet() :
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
                time.sleep(0.1)
            time.sleep(0.1)
