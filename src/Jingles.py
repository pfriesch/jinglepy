import time
import vlc
import config


class Jingles:
    def __init__(self, audiofile):
        self.player = vlc.MediaPlayer(audiofile)
        self.player.play()
        time.sleep(0.1)
        self.duration = round(self.player.get_length() / 1000, 1)
        self.player.stop()

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def stop(self):
        self.player.stop()

    def get_duration(self):
        return self.duration
