# Times in minutes
from typing import List

from src.helper import ScheduleEntry, TournamentState

gameLength = 300
nLastMinutes = 30
breakLength = 5

# Time of day the first match starts. String has to be of the format "dd.mm.yy HH:MM:SS"
tournamentStartTime = "10.08.22 00:50:00"  # Starttime as "dd.mm.yy hh:mm:ss"
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

# time format "dd.mm.yy hh:mm:ss"
schedule: List[ScheduleEntry] = [
    ScheduleEntry("10.08.22 00:50:00", TournamentState.NotStarted),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Break),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Match),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Break),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Match),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Break),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Match),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Break),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Match),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Break),
    ScheduleEntry("10.08.22 00:50:00", TournamentState.Match)
]
