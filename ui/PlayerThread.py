import queue
import threading
import time
from datetime import datetime
from queue import Queue

import vlc

from ui.NativeVolumeControls import NativeVolumeControls
from ui.helper import JingleEntry
import config


class PlayerThread(threading.Thread):
    def __init__(self, jingle_queue: Queue[JingleEntry]):
        threading.Thread.__init__(self)
        self.queue: Queue[JingleEntry] = jingle_queue

    @classmethod
    def clem_change_vol(cls, start_vol, end_vol):
        diff = start_vol - end_vol
        steps = 4
        step = diff / steps
        cur_vol = start_vol
        for i in range(steps):
            cur_vol = cur_vol - step
            volume_control = NativeVolumeControls()
            volume_control.volume_set(cur_vol)
        time.sleep(.01)

    def run(self):
        while True:
            try:
                next_jingle = self.queue.get()
                volume_control = NativeVolumeControls()
                cur_clem_vol = volume_control.volume_get()
                clem_vol = 0
                if cur_clem_vol != 0:
                    clem_vol = cur_clem_vol
                    PlayerThread.clem_change_vol(cur_clem_vol, 0)

                volume_control.stop()
                volume_control.volume_set(clem_vol)

                player = vlc.MediaPlayer(config.jingles[next_jingle.jingle_id])
                player.play()
                time.sleep(next_jingle.duration.total_seconds())
                player.stop()
                volume_control.volume_set(0)

                volume_control.play()
                PlayerThread.clem_change_vol(0, cur_clem_vol)
            except queue.Empty:
                pass
            except ValueError as e:
                print(e)
