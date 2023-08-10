from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import List

import librosa

import config


class TournamentState(Enum):
    NotStarted = "Not Started"
    Match = "Match"
    Break = "Break"
    Finished = "Finished"


@dataclass
class ScheduleEntry:
    segment_start: datetime
    segment_end: datetime
    starts_segment: TournamentState

    def __str__(self):
        return self.segment_start.strftime(config.dateformat) + " - " + self.segment_end.strftime(config.dateformat) + "  " + self.starts_segment.value


@dataclass
class JingleEntry:
    jingle_id: str
    timestamp: datetime
    duration: timedelta
    enqueued: bool = False

    def __str__(self):
        return (self.timestamp - self.duration).strftime(config.dateformat) + " - " + self.timestamp.strftime(config.dateformat) + "  " + self.jingle_id


def _compute_schedule() -> List[ScheduleEntry]:
    schedule = [
        ScheduleEntry(config.tournament_start_time - config.breakLength - config.breakLength, config.tournament_start_time - config.breakLength, TournamentState.NotStarted),
    ]

    current_match_start_time: datetime = config.tournament_start_time

    for slot in range(config.slots_count):
        schedule.append(ScheduleEntry(current_match_start_time - config.breakLength, current_match_start_time, TournamentState.Break))
        schedule.append(ScheduleEntry(current_match_start_time, current_match_start_time + config.gameLength, TournamentState.Match))

        current_match_start_time = current_match_start_time + config.gameLength + config.breakLength

    return schedule


def _compute_jingle_schedule(schedule: List[ScheduleEntry]) -> List[JingleEntry]:
    jingle_schedule = []

    for schedule_entry in schedule:

        if schedule_entry.starts_segment == TournamentState.Break:
            jingle_schedule.append(JingleEntry("5minToGame", schedule_entry.segment_end - config.fiveMinToGame, timedelta(seconds=librosa.get_duration(path=config.jingles["5minToGame"]))))
            jingle_schedule.append(JingleEntry("1minToGame", schedule_entry.segment_end - config.oneMinToGame, timedelta(seconds=librosa.get_duration(path=config.jingles["1minToGame"]))))

        elif schedule_entry.starts_segment == TournamentState.Match:
            jingle_schedule.append(JingleEntry("gamesStarting", schedule_entry.segment_start, timedelta(seconds=librosa.get_duration(path=config.jingles["gamesStarting"]))))
            jingle_schedule.append(JingleEntry("halfTime", schedule_entry.segment_start + config.halfTime, timedelta(seconds=librosa.get_duration(path=config.jingles["halfTime"]))))
            jingle_schedule.append(JingleEntry("5minLeft", schedule_entry.segment_end - config.fiveMinLeft, timedelta(seconds=librosa.get_duration(path=config.jingles["5minLeft"]))))
            jingle_schedule.append(JingleEntry("1minLeft", schedule_entry.segment_end - config.oneMinLeft, timedelta(seconds=librosa.get_duration(path=config.jingles["1minLeft"]))))
            jingle_schedule.append(JingleEntry("gameOver", schedule_entry.segment_end, timedelta(seconds=librosa.get_duration(path=config.jingles["gameOver"]))))

    prev_start = datetime.fromtimestamp(0)
    prev_end = datetime.fromtimestamp(0)

    for je in jingle_schedule:
        start = je.timestamp - je.duration
        end = je.timestamp

        if start > end:
            raise Exception(f"Invalid schedule: start > end {start} > {end} {je.jingle_id}")

        if prev_start > start:
            raise Exception(f"Invalid schedule: prev_start > start {prev_start} > {start} {je.jingle_id}")

        if prev_end > start:
            raise Exception(f"Invalid schedule: prev_end > start {prev_end} > {start} {je.jingle_id}")

        prev_start = start
        prev_end = end

    return jingle_schedule


schedule = _compute_schedule()
jingle_schedule = _compute_jingle_schedule(schedule)
