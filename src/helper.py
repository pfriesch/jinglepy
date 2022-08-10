import time
import dataclasses
from enum import Enum

from .NativeVolumeControls import NativeVolumeControls


class TournamentState(Enum):
    NotStarted = "NotStarted"
    Match = "Match"
    Break = "Break"


@dataclasses
class ScheduleEntry:
    timestamp: str  # "dd.mm.yy HH:MM:SS"
    starts_segment: TournamentState

    def timestamp(self):
        int(time.mktime(time.strptime(self.timestamp, "%d.%m.%y %H:%M:%S")))


def formated_time(t):
    return time.strftime("%H:%M:%S", time.localtime(t))


volume_control = NativeVolumeControls()
