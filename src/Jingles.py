from datetime import timedelta

import vlc
import config
from src.helper import thread_sleep


class Jingles:
    def __init__(self, audiofile):
        self.player = vlc.MediaPlayer(audiofile)
        self.player.play()
        thread_sleep(0.1)
        self.duration = timedelta(milliseconds=self.player.get_length())
        self.player.stop()

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def get_duration(self) -> timedelta:
        return self.duration
