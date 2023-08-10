from datetime import datetime

from rich.panel import Panel

from textual.reactive import Reactive
from textual.widget import Widget
from queue import Queue, Empty

import config
from ui.helper import schedule, jingle_schedule, JingleEntry
from ui.PlayerThread import PlayerThread

from textual.widgets import Placeholder
from rich import box

wheel = ["🎺", "🎷"]


class JingleQueue(Widget):
    mouse_over = Reactive(False)

    jingle_schedule = Reactive([])

    def __init__(self, *, name: str | None = None, height: int | None = None) -> None:
        super().__init__(name="JingleQueue")
        self.height = height
        self.jingle_queue: Queue[JingleEntry] = Queue()

    def on_mount(self):
        self.set_interval(1, self.refresh)
        self.ps = PlayerThread(self.jingle_queue)
        self.ps.start()

    def render(self) -> Panel:

        lines = []

        now = datetime.now()

        if not self.ps.is_alive():
            self.ps = PlayerThread(self.jingle_queue)
            self.ps.start()
            lines.append("!!! PLAYER NOT RUNNING RESTART THE APP !!!!")

        if len(jingle_schedule) == 0:
            lines.append("FAILED TO LOAD JINGLES")
        for j in jingle_schedule:
            if j.timestamp < datetime.now() - ((config.gameLength + config.breakLength) * 2):
                continue
            duration = j.duration
            if now > j.timestamp:
                lines.append("✅  " + str(j))
            elif now > j.timestamp - duration:
                if not j.enqueued:
                    j.enqueued = True
                    self.jingle_queue.put_nowait(j)
                lines.append(wheel[int(datetime.now().timestamp()) % 2] + "  " + str(j))

            else:
                lines.append("    " + str(j))

        content = "\n".join(lines)

        return Panel(
            content,
            title=self.__class__.__name__,
            border_style="green",
            box=box.HEAVY,
            height=self.height,
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
