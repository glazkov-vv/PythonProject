from collections.abc import Hashable
from typing_extensions import Literal
import urwid
import asyncio
import time

from cli.error import ErrorWindow
from cli.manager import Manager
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
        self._columnContent=[]
        ops=self.data
        for (method,sz,type) in self.__class__.schema:
            if (type=='content'):
                value=ops.__getattribute__(method)()
                text=urwid.Text(value,wrap='ellipsis')
                self._columnContent.append(('weight',sz,text))
            elif (type =='method'):
                self._columnContent.append(('weight',sz,self.__getattribute__(method)()))
        
        self._columns=urwid.Columns(self._columnContent)
        self._columns=urwid.AttrMap(self._columns,"normal","reversed")
    

    def reload_data(self):
        i=0
        ops=self.data
        for (method,sz,type) in self.__class__.schema:
            if (type=='content'):
                self._columnContent[i][2].set_text(ops.__getattribute__(method)())
            elif (type =='method'):
                self._columnContent[i][2].update_data()
            i+=1

    def render(self, size: tuple[int], focus: bool = False) -> urwid.Canvas:
        (maxcol,) = size
        self.reload_data()
        return self._columns.render(size,focus)

class Selectable(urwid.Text):
    def __init__(self, custom_data:dict) -> None:
        self._custom_data=custom_data.copy()
        super().__init__("(*)" if self._custom_data["FileEntry"].is_selected() else "( )",align='center')

    _selectable=True

    def update_data(self):
        super().set_text("(*)" if self._custom_data["FileEntry"].is_selected() else "( )")
    
    def mouse_event(self, size: tuple[()] | tuple[int] | tuple[int, int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
       if (button==1 and event=='mouse press'):
            self._custom_data["FileEntry"].revert_selection()
    
    def selectable(self) -> bool:
        return True
    def render(self, size: tuple[int] | tuple[()], focus: bool = False) -> urwid.TextCanvas:
        return super().render(size, focus)

class FileName(urwid.Widget):
    def rows(self,size,focus):
        return 1
    def get_normal(self)->str:
        return self._custom_data["FileEntry"].get_color()
    def get_focused(self)->str:
        return "rev "+self.get_normal()
    def __init__(self, custom_data:dict) -> None:
        super().__init__()
        self._custom_data=custom_data.copy()
        self._text=urwid.Text(self._custom_data["FileEntry"].data.get_name(),wrap='ellipsis')
        
    def update_data(self):
        self._text=urwid.Text(self._custom_data["FileEntry"].data.get_name(),wrap='ellipsis')

    _selectable:False

    def selectable(self) -> bool:
        return False

    def render(self, size: tuple[int] | tuple[()], focus: bool = False) -> urwid.TextCanvas:
        mp=urwid.AttrMap(self._text,{None:(self.get_focused() if self._custom_data["FileEntry"].focused else self.get_normal())})
        return mp.render(size,focus)
        


class FileEntry(TableEntry):
    def __init__(self,custom_data, data:File,pos:int,workspace:Workspace) -> None:
        data.subscribe(self.rebuild)
        self._custom_data=custom_data.copy()
        self.pos=pos
        self._lastClick=0
        self._workspace=workspace
        self._custom_data["FileEntry"]=self
        self.focused=False
        super().__init__(data)



    
    def is_selected(self)->bool:
        return self.data.getSelected()

    def get_selectable(self)->Selectable:
        return Selectable(self._custom_data)
    
    def get_file_name(self)->FileName:
        return FileName(self._custom_data)
    
    schema=[("get_file_name",4,'method'),("getFormattedSize",1,'content'),("get_selectable",0.5,'method')]

    def revert_selection(self)->None:
        self.data.setSelected(not self.data.getSelected())


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
       return self._columns.mouse_event(size,event,button,col,row,focus)
    

    def get_color(self)->str:
        if (self.data.isDir()):
            return "folds"
        if (self.data.is_executable()):
            return "execs"

    def step_in(self)->None:
        
        if (self.data.isDir()):
            #content.update(self.data.getPath(),self.pos)
            res=self._workspace.step_in(self.data.getPath())
            if (res!=None):
                self._custom_data["TwoTabs"].push_on_stack(ErrorWindow(res))
        

    def keypress(self,size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        super().keypress(size,key)
        if (key=='enter'):
            self.step_in()
        if (key=='f12' and Manager.get_lock()==None):
            pw=PropertyWindow(self.data)
            self._custom_data["viewstack_push_function"](pw)
        if (key==' ' and Manager.get_lock()==None):
            self.revert_selection()
            #self._invalidate()
        return super().keypress(size,key)

    def render(self, size: tuple[int], focus: bool = False) -> urwid.Canvas:
        inv=False
        if (self.focused!=focus):
            inv=True
        self.focused=focus
        if inv:
            for h in self._columnContent:
                h[2]._invalidate()
        return super().render(size, focus)