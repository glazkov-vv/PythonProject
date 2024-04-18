from __future__ import annotations
import debugpy
import time
from os import listdir
import os
import os.path
from os.path import isfile, join
import urwid


# Allow other computers to attach to debugpy at this IP address and port.
debugpy.listen(('0.0.0.0', 5678))
print("Waiting for debugger to attach...")

# Pause the script until a debugger is attached
debugpy.wait_for_client()





def exit_on_q(key):
    if key in {"q", "Q"}:
        present=top.contents
        updated=[present[0],(build_list(),present[1][1])]
        top.contents[1]=(build_list(),present[1][1])
        top.top_w=build_list()
        top._invalidate()
        loop.draw_screen()


palette = [
    ("banner", "", "", "", "#ffa", "#60d"),
    ("streak", "", "", "", "g50", "#60a"),
    ("inside", "", "", "", "g38", "#808"),
    ("outside", "", "", "", "g27", "#a06"),
    ("bg", "", "", "", "g7", "#d06"),
]   

lastTbx=0


class File:
    _path:str
    def getSize(self)->int | None:
        return os.path.getsize(self._path)
    
    def getFormattedSize(self)->str:
        sz=self.getSize()
        if sz is None:
           return ""
        sfx=["bytes","KB","MB","GB","TB"]
        pos=0
        while sz>=1024:
            sz/=1024
            pos+=1
        return "{:.2f}".format(sz)+" "+sfx[pos]
    
    def isDir(self)->bool:
        return os.path.isdir(self._path)

    @staticmethod
    def fromPath(path:str)->str:
        file=File()
        file._path=path
        return file

    def getPath(self)->str:
        return self._path



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
    schema=[("getPath",4),("getFormattedSize",1)]
    def mouse_event(self,size: tuple[int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
       #print ("KABOOM")
       if (not focus and self.data.isDir()):
           pass
           #raise urwid.ExitMainLoop()
       
class TwoTabs(urwid.widget):
    def render(self, size: tuple[int,int], focus: bool = False) -> urwid.Canvas:
        (maxcol,maxrow) = size

        left=build_list(build_table())
        


def build_table()->iterable[File]:
    return [File.fromPath(h) for h in listdir()]

def build_list(fileEntries:iterable[File]) -> urwid.ListBox:
    space_distr=[0.6,0.4]
    finres=[]
    for h in fileEntries:
        temp=FileEntry(h)
        finres.append(temp)
    lbx=urwid.ListBox(finres)
    lbx.set_focus(0)
    ans=urwid.Filler(lbx,height=20)
    return ans

list=build_list(build_table())
top = urwid.Overlay(
    list,
    urwid.SolidFill("\N{MEDIUM SHADE}"),
    align=urwid.CENTER,
    width=(urwid.RELATIVE, 85),
    valign=urwid.MIDDLE,
    height=(urwid.RELATIVE, 85),
    min_width=20,
    min_height=9,
)

loop=urwid.MainLoop(top,palette=[("reversed", "standout", "")],unhandled_input=exit_on_q)
loop.run()