
class Ui:
    def __init__(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(1)

        self.sss = self.stdscr.getmaxyx()

        self.main_window = curses.newwin(self.sss[0] - 10, self.sss[1] - 30, 0, 0)
        self.match_window = curses.newwin(self.sss[0] - 10, 30, 0, self.sss[1] - 30)
        self.break_panel = curses.panel.new_panel(self.match_window)
        self.break_window = curses.newwin(self.sss[0] - 10, 30, 0, self.sss[1] - 30)
        self.match_panel = curses.panel.new_panel(self.break_window)

        self.break_panel.hide()

    def refresh(self):
        curses.panel.update_panels()
        self.main_window.refresh()
        self.match_window.refresh()
        self.break_window.refresh()

    def swpan(self, from_panel, to_panel):

        from_panel.bottom()
        from_panel.hide()
        to_panel.top()
        to_panel.show()

    def switch_pan(self):

        def switch(from_panel, to_panel):
            from_panel.bottom()
            from_panel.hide()
            to_panel.top()
            to_panel.show()

        if self.break_panel.hidden():
            switch(self.match_panel, self.break_panel)
        else:
            switch(self.break_panel, self.match_panel)

        self.refresh()

    def quit_ui(self):
        curses.nocbreak()
        self.stdscr.keypad(0)
        curses.curs_set(1)
        curses.echo()
        curses.endwin()
        exit(0)
