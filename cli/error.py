import asyncio
import urwid

from cli.stackedview import StackedView

class ErrorWindow(urwid.Filler,StackedView):
    _selectable=True
    def selectable(self) -> bool:
        return True

    def __init__(self, value) -> None:
        self._updated_event=asyncio.Event()
        message=urwid.Text(value+"\n\n"+"Press Enter to exit",align="center")


        super().__init__(message)
    
    def keypress(self, size: tuple[int, int] | tuple[()], key: str) -> str | None:
        if (key=='enter'):
            self.pop_on_stack()
            return None
        return super().keypress(size, key)
    
