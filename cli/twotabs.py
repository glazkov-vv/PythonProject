import urwid
from logic.file import *
from logic.workspace import *
from cli.filepanel import *

class TwoTabs(urwid.WidgetContainerMixin,urwid.Widget):
    _selectable=False

    def selectable(self)->bool:
        return True
    def __init__(self,active_workspaces) -> None:
        super().__init__()

        active_workspaces[0]=Workspace("/home")
        active_workspaces[1]=Workspace("/home")
        left=FilePanel(active_workspaces[0],0)
        right=FilePanel(active_workspaces[1],1)
        active_workspaces[0].subscribe(left.rebuild)
        active_workspaces[1].subscribe(right.rebuild)
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
    
    """ def update(self,path,num)->None:
        active_workspaces[num]=Workspace(path)
        self.contents[0][0].contents[num]=(FilePanel(active_workspaces[num],num),self.contents[0][0].contents[num][1])
        self._invalidate() """
   

