import time

from src.Feeder import Feeder
from src.Jingles import Jingles

if __name__ == "__main__":

    jingle = Jingles("ressources/220809_TournaMINT_Jingles_1 minute left.wav")
    jingle.play()
    time.sleep(500)
    # f = Feeder()
    # f.run()
