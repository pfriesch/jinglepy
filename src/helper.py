import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .NativeVolumeControls import NativeVolumeControls


class TournamentState(Enum):
    NotStarted = "NotStarted"
    Match = "Match"
    Break = "Break"
    Finished = "Finished"


@dataclass
class ScheduleEntry:
    timestamp: str  # "dd.mm.yy HH:MM:SS"
    starts_segment: TournamentState

    def datetime(self) -> datetime:
        return datetime.strptime(self.timestamp, "%d.%m.%y %H:%M:%S")


volume_control = NativeVolumeControls()


def thread_sleep(secs: float):
    time.sleep(secs)
