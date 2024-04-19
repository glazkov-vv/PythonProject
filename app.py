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
    _selected:bool
    def getSize(self)->int | None:
        return os.path.getsize(self._path)
    
    def getSelectedFormatted(self)->str:
        return "(*)" if self._selected else "( )"
    def getSelected(self)->bool:
        return self._selected

    def setSelected(self,value:bool)->None:
        self._selected=value
        

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
        file._selected=False
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
    def __init__(self, data,pos) -> None:
        super().__init__(data)
        self.pos=pos
        self._lastClick=0

    schema=[("getPath",4),("getFormattedSize",1),("getSelectedFormatted",0.5)]

    def doubleClick(self)->None:
        self.step_in()

    def mouse_event(self,size: tuple[int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
       #print ("KABOOM")
       if (button==1 and event=="mouse press"):
            if (time.time()-self._lastClick<200):
                self.doubleClick()
            self._lastClick=time.time()
        
        
       if (not focus and self.data.isDir()):
           pass
           #raise urwid.ExitMainLoop()

    def step_in(self)->None:
        if (self.data.isDir()):
            content.update(self.data.getPath(),self.pos)
    
    def keypress(self,size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        super().keypress(size,key)
        if (key=='enter'):
            self.step_in()
        if (key==' '):
            self.data.setSelected(not self.data.getSelected())
            self._invalidate()
        return super().keypress(size,key)
   
class TwoTabs(urwid.WidgetContainerMixin,urwid.Widget):
    _selectable=False

    def selectable(self)->bool:
        return True
    def __init__(self) -> None:
        super().__init__()
        left=FilePanel("/home",0)
        right=FilePanel("/home",1)
        #right=build_list(build_table("/"))
        res=urwid.Columns([left,right],dividechars=3)
        self.contents=[(res,None)]
        

    def triggerFocusChange(self)->bool:
        self.contents[0][0].focus_position^=1
        return True
    
    def keypress(self,size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        
        if key=='tab':
            self.contents[0][0].focus_position^=1

        return self.contents[0][0].focus.keypress(size,key)
        

    def mouse_event(self,size: tuple[()] | tuple[int] | tuple[int, int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
            return self.contents[0][0].mouse_event(size,event,button,col,row,True)

    def render(self, size: tuple[int,int], focus: bool = False) -> urwid.Canvas:
        (maxcol,maxrow) = size
        
        return self.contents[0][0].render(size,focus)
    
    def update(self,path,num)->None:
        self.contents[0][0].contents[num]=(FilePanel(path,num),self.contents[0][0].contents[num][1])
        self._invalidate()
   



def build_table(path=None)->iterable[File]:
    return [File.fromPath(os.path.join("" if path is None else path,h)) for h in listdir(path)]


class FilePanel(urwid.Filler):

    def __init__(self,path=None,pos=0) -> None:
        self._path=path
        self.pos=pos
        temp=build_table(path)
        lbx=urwid.ListBox([FileEntry(h,self.pos) for h in temp])
        super().__init__(lbx,height=20)
        self._lastClick=0
    
    _path:str

    def getPath(self)->str:
        return self._path
    def update(self)->None:
        temp=build_table(self._path)
        lbx=urwid.ListBox([FileEntry(h,self.pos) for h in temp])
        self.body=lbx
    

    
    def keypress(self, size: tuple[int, int] | tuple[()], key: str) -> str | None:
        if (key=='left'):
            self._path=os.path.dirname(self._path)
            self.update()
            return None
        return super().keypress(size, key)

    def doubleClick():
        pass
    def mouse_event(self, size: tuple[int, int] | tuple[int], event, button: int, col: int, row: int, focus: bool) -> bool | None:
        
        return super().mouse_event(size, event, button, col, row, focus)



def build_list(fileEntries:iterable[File]) -> urwid.ListBox:
    space_distr=[0.6,0.4]
    finres=[]
    for h in fileEntries:

        temp=FileEntry(h,1)
        finres.append(temp)
    lbx=urwid.ListBox(finres)
    #lbx.set_focus(0)
    ans=urwid.Filler(lbx,height=20)
    return ans

#list=build_list(build_table())
content=TwoTabs()   
top = urwid.Overlay(
    content,
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