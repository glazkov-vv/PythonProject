import asyncio
import urwid

from cli.manager import Manager
from cli.stackedview import StackedView


class ProgressWindow(urwid.Filler, StackedView):
    _selectable = True

    def selectable(self) -> bool:
        return True

    def __init__(self) -> None:
        self._updated_event = asyncio.Event()

        message = urwid.Text("OPERATION IN PROGRESS", 'center')
        self._progress_bar = urwid.ProgressBar(None, 'reversed', 0, 100)
        ops = urwid.Pile([message, self._progress_bar])

        super().__init__(ops)

    def callback(self, value: float) -> None:
        # self.set_body(urwid.Text(f"Progress {str(value)}"))
        self._progress_bar.current = int(value * 100)
        Manager.loop.draw_screen()
