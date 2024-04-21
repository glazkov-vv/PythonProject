import urwid

import time

from cli.props import PropertyWindow, PropertyWindowMock
from logic.file import File
from logic.workspace import Workspace


class TableEntry(urwid.Widget):
    def rows(self, size: tuple[int], focus: bool = False) -> int:
        return 1
    _selectable = True

    
    def __init__(self,data) -> None:
        super().__init__()
        self.data=data

    def render(self, size: tuple[int], focus: bool = False) -> urwid.Canvas:
        (maxcol,) = size
        
        ops=self.data
        
        columnContent=[]
        for (method,sz) in self.__class__.schema:
            value=ops.__getattribute__(method)()
            text=urwid.Text(value,wrap='ellipsis')
            columnContent.append(('weight',sz,text))
        
        cols=urwid.Columns(columnContent)
        cols=urwid.AttrMap(cols,None,"reversed")

        return cols.render(size,focus)

class FileEntry(TableEntry):
    def __init__(self,custom_data, data:File,pos:int,workspace:Workspace) -> None:
        super().__init__(data)
        data.subscribe(self.rebuild)
        self._custom_data=custom_data
        self.pos=pos
        self._lastClick=0
        self._workspace=workspace

    schema=[("getPath",4),("getFormattedSize",1),("getSelectedFormatted",0.5)]

    def doubleClick(self)->None:
        self.step_in()

    def rebuild(self)->None:
        self._invalidate()

    def mouse_event(self,size: tuple[int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
       #print ("KABOOM")
       if (button==1 and event=="mouse press"):
            if (time.time()-self._lastClick<0.2):
                self.doubleClick()
            self._lastClick=time.time()
        
        
       if (not focus and self.data.isDir()):
           pass
           #raise urwid.ExitMainLoop()

    def step_in(self)->None:
        if (self.data.isDir()):
            #content.update(self.data.getPath(),self.pos)
            self._workspace.step_in(self.data.getPath())
    

    def keypress(self,size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        super().keypress(size,key)
        if (key=='enter'):
            self.step_in()
        if (key=='f12'):
            pw=PropertyWindow(self.data)
            self._custom_data["viewstack_push_function"](pw)
        if (key==' '):
            self.data.setSelected(not self.data.getSelected())
            #self._invalidate()
        return super().keypress(size,key)
