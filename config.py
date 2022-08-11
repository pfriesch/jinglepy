# Times in minutes
from datetime import timedelta, datetime

gameLength = timedelta(minutes=3)
halfTime = timedelta(seconds=30)
oneMinLeft = timedelta(seconds=30)
oneMinToGame = timedelta(seconds=30)
fiveMinLeft = timedelta(seconds=60)
fiveMinToGame = timedelta(seconds=60)
breakLength = timedelta(minutes=2)

# Time of day the first match starts. String has to be of the format "dd.mm.yy HH:MM:SS"
# tournament_start_time = datetime(year=2022, month=8, day=11, hour=21, minute=23, second=00)
tournament_start_time = datetime.now() - timedelta(seconds=1000)
# tournament_start_time = datetime(year=tournament_start_time.year, month=tournament_start_time.month, day=tournament_start_time.day, hour=tournament_start_time.hour, minute=15 * round((float(tournament_start_time.minute) + float(tournament_start_time.second) / 60) / 15) % 60)

slots_count = 9
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

# dateformat = "%H:%M"
dateformat = "%H:%M:%S"

tournament_start_time = datetime(year=tournament_start_time.year, month=tournament_start_time.month, day=tournament_start_time.day, hour=0, minute=0)

gameLength = timedelta(minutes=45)
halfTime = timedelta(minutes=22)
oneMinLeft = timedelta(minutes=1)
oneMinToGame = timedelta(minutes=1)
fiveMinLeft = timedelta(minutes=5)
fiveMinToGame = timedelta(minutes=5)
breakLength = timedelta(minutes=15)
