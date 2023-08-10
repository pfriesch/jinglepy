import datetime
import sys

from textual.app import App, ComposeResult

from ui.JingleQueue import JingleQueue
from ui.Schedule import Schedule
from textual.widgets import Footer

from textual.app import App, ComposeResult
from textual import events
from textual.widgets import RichLog

log_filename = "log.log"


class PrintLogger(RichLog):
    """A RichLog which captures printed text."""

    def on_print(self, event: events.Print) -> None:
        if event.text != "\n":
            with open(log_filename, 'a') as the_file:
                the_file.write(f"[{str(datetime.datetime.now())}] {event.text}\n")


class Ui(App):
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "jinglepy.css"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield PrintLogger()
        yield JingleQueue()
        yield Schedule()
        yield Footer()

    def on_mount(self) -> None:
        # self.query_one(RichLog).write("RichLog")
        self.query_one(RichLog).begin_capture_print()


try:
    log_filename = str(datetime.datetime.now()) + "-log.log"
    app = Ui()
    # app.begin_capture_print()
    app.run()


except Exception as e:
    print(e)
    sys.exit(3)
