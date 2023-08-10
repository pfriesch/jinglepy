from datetime import datetime

from rich.panel import Panel

from textual.reactive import Reactive
from textual.widget import Widget

import config
from ui.helper import schedule
from rich import box

wheel = ["♻️ ", "🌀︎"]


class Schedule(Widget):
    mouse_over = Reactive(False)

    current_time = Reactive(datetime.now())
    schedule = Reactive([])

    def __init__(self, *, name: str | None = None, height: int | None = None) -> None:
        super().__init__(name="Schedule")
        self.height = height

    def on_mount(self):
        self.set_interval(1, self.refresh)

    def render(self) -> Panel:

        lines = []
        now = datetime.now()
        for s in schedule:
            if now > s.segment_end:
                lines.append("✅  " + s.segment_start.strftime(config.dateformat) + "  " + str(s.starts_segment.value))
            elif now > s.segment_start:
                lines.append(wheel[int(datetime.now().timestamp()) % 2] + "  " + s.segment_start.strftime(config.dateformat) + "  " + str(s.starts_segment.value))

            else:
                lines.append("    " + s.segment_start.strftime(config.dateformat) + "  " + str(s.starts_segment.value))

        content = f"""Current Time :  {datetime.now().strftime("%H:%M:%S")}\n\n""" + "\n".join(lines)

        return Panel(
            content,
            title=self.__class__.__name__,
            border_style="green",
            box=box.HEAVY ,
            height=self.height,
        )

    def on_enter(self) -> None:
        self.mouse_over = True

    def on_leave(self) -> None:
        self.mouse_over = False
