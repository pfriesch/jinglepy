# Times in minutes
from datetime import timedelta
from typing import List

from src.helper import ScheduleEntry, TournamentState
from scheudle_test import schedule_test

gameLength = timedelta(minutes=2)
halfTime = timedelta(seconds=30)
oneMinLeft = timedelta(seconds=30)
oneMinToGame = timedelta(seconds=30)
fiveMinLeft = timedelta(seconds=60)
fiveMinToGame = timedelta(seconds=60)
breakLength = timedelta(seconds=60)

# Time of day the first match starts. String has to be of the format "dd.mm.yy HH:MM:SS"
tournamentStartTime = "11.08.22 02:30:00"  # Starttime as "dd.mm.yy hh:mm:ss"
# gameLength = 23  # times in minutes
# nLastMinutes = 5  # times in minutes
# breakLength = 2  # times in minutes

# jingles
jingles = {
    "1minLeft": "ressources/220809_TournaMINT_Jingles_1 minute left.wav",
    "1minToGame": "ressources/220809_TournaMINT_Jingles_1 minute to game.wav",
    "5minLeft": "ressources/220809_TournaMINT_Jingles_5 minutes left.wav",
    "5minToGame": "ressources/220809_TournaMINT_Jingles_5 minutes to game.wav",
    "gameOver": "ressources/220809_TournaMINT_Jingles_Games are over.wav",
    "gamesStarting": "ressources/220809_TournaMINT_Jingles_Games are starting.wav",
    "halfTime": "ressources/220809_TournaMINT_Jingles_Half time.wav"
}

# schedule = schedule_test
