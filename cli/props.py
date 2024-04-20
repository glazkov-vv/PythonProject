import urwid
from logic.file import *

class PropertyWindow(urwid.Widget):
    def __init__(self,file:File) -> None:
        super().__init__()
        self._file=file
    
    def rows(self, size: tuple[int], focus: bool = False) -> int:
        return 1
    
    def render(self, size: tuple[()] | tuple[int] | tuple[int, int], focus: bool = False) -> urwid.Canvas:
        name=urwid.Edit(self._file.get_name())
        sep1=urwid.Divider("-")

        pile=urwid.Pile([name,sep1])
    
    