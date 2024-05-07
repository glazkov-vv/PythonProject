import asyncio
import urwid
from cli.error import ErrorWindow
from logic.transactions import MoveTransaction, RemoveTransaction
from logic.workspace import *
from cli.entry import *
import typing

class FilePanel(urwid.Filler):



    def __init__(self,custom_data,workspace:Workspace,pos:int=0) -> None:
        self._workspace=workspace
        self.pos=pos
        self._custom_data=custom_data.copy()
        self._custom_data["FilePanel"]=self
        self._custom_data["Workspace"]=workspace
        self._infocus=None
        #temp=build_table(path)

        
        #lbx=urwid.ListBox([PanelPath(self._custom_data)]+[TitleEntry(self._custom_data)]+[urwid.BoxAdapter(urwid.ListBox([FileEntry(self._custom_data,h,self.pos,workspace) for h in workspace.get_contents()]),height=('relative',100))])
        
        lbx=urwid.ListBox([FileEntry(self._custom_data,h,self.pos,workspace) for h in workspace.get_contents()])

        
        top=urwid.Pile([PanelPath(self._custom_data),TitleEntry(self._custom_data)],)
        cont=urwid.Frame(lbx,header=top)

        super().__init__(cont,height=('relative',80))
        self._lastClick=0
    
    _path:str

    def get_sort(self)->tuple[None|str,None|Literal["asc","desc"]]:
        return self._workspace.get_sort()

    def report_focus(self,child:urwid.Widget):
        if (self._infocus!=child):
            if (self._infocus!=None):
                self._infocus.clear_focus()
            self._infocus=child
    

    def getPath(self)->str:
        return self._workspace.get_path()
    """ def update(self)->None:
        temp=build_table(self._path)
        lbx=urwid.ListBox([FileEntry(h,self.pos) for h in temp])
        self.body=lbx """
    
    

    def rebuild(self,in_focus:bool=False)->None:
        lbx=urwid.ListBox([FileEntry(self._custom_data,h,self.pos,self._workspace) for h in self._workspace.get_contents()])

        
        top=urwid.Pile([PanelPath(self._custom_data),TitleEntry(self._custom_data)],)
        cont=urwid.Frame(lbx,header=top)


        oldpath=self.body.get_focus_path()
        self.body=cont

        if (in_focus):
            #pass
            self.body.set_focus_path(oldpath)
            
            #self.body.focus_position=1
            self.body.set_focus_pending=None
            #titleentry=self.body.body.contents[1]
            #cols=titleentry.contents[0][0]
            
        
        self._invalidate()

        #self.body.set_focus_path(oldpath)
    
    def _start_selection(self,mode)->None|str:
        Manager.active_selection=self._workspace.get_selection()
        if (Manager.active_selection.empty()):
            async def fun():
                self._custom_data["TwoTabs"].push_on_stack(ErrorWindow("No files selected"))
                await self._custom_data["TwoTabs"]._updated_event.wait()
            asyncio.create_task(fun())
        else:
            Manager.set_lock(self.pos^1)
            Manager.operation_mode=mode
        return None

    



    def keypress(self, size: tuple[int, int] | tuple[()], key: str) -> str | None:
        if (key=='esc'):
            Manager.set_lock(None)
        
        if (key=='delete' and Manager.operation_mode=='normal'):
            sel=self._workspace.get_selection()
            asyncio.create_task(self._custom_data["TwoTabs"].execute_transaction(RemoveTransaction(sel)))
            return None

        if (key=='t' and Manager.operation_mode=='normal'):
            self._workspace.set_tree(not self._workspace.get_tree())

        if (key=='m'):
            asyncio.create_task(self._custom_data["TwoTabs"].mkdir(self.getPath()))
            return None

        if (key=='x' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_move")
            #self.contents[0][0]
        if (key=='c' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_copy")

        if (key=='backspace'):
            res=self._workspace.step_up()
            if (res!=None):
                asyncio.create_task(self._custom_data["TwoTabs"].push_on_stack(ErrorWindow(res)))
            return None
        
        return super().keypress(size, key)

    def render(self, size: tuple[int, int] | tuple[int], focus: bool = False) -> urwid.CompositeCanvas:
        return super().render(size, focus)
    

    def doubleClick():
        pass
    def mouse_event(self, size: tuple[int, int] | tuple[int], event, button: int, col: int, row: int, focus: bool) -> bool | None:
        
        return super().mouse_event(size, event, button, col, row, focus)

