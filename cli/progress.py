from asyncio import Event
import urwid

from cli.stackedview import StackedView
class ProgressWindow(urwid.SolidFill,StackedView):
    def __init__(self) -> None:
        self._updated_event=Event()
        super().__init__('X')