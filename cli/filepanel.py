import asyncio
import urwid
from cli.error import ErrorWindow
from logic.transactions import MoveTransaction, RemoveTransaction
from logic.workspace import *
from cli.entry import *

def sigtest():
    pass

class FilePanel(urwid.Filler):



    def __init__(self,custom_data,workspace:Workspace,pos:int=0) -> None:
        self._workspace=workspace
        self.pos=pos
        self._custom_data=custom_data.copy()
        self._custom_data["FilePanel"]=self
        self._custom_data["Workspace"]=workspace
        self._infocus=None
        #temp=build_table(path)

        lbx=urwid.ListBox([TitleEntry(self._custom_data)]+[FileEntry(self._custom_data,h,self.pos,workspace) for h in workspace.get_contents()])
        super().__init__(lbx,height=('relative',80))
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
    

    def rebuild(self,in_focus=None)->None:
        lbx=urwid.ListBox([TitleEntry(self._custom_data)]+[FileEntry(self._custom_data,h,self.pos,self._workspace) for h in self._workspace.get_contents()])
        self.body=lbx

        if (in_focus!=None):
            def calc_by_name(widget,name):
                for i in range(len(widget.contents)):
                    h=widget.contents[i][0]
                    if (h._prop==name):
                        return i
            ops=[0,0,calc_by_name(self.body.body.contents[0].contents[0][0],in_focus)]
            self.body.set_focus_path(ops)
        self._invalidate()

    
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

            

        if (key=='x' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_move")
            #self.contents[0][0]
        if (key=='c' and Manager.operation_mode=="normal"):
            return self._start_selection("select_for_copy")

        if (key=='left'):
            res=self._workspace.step_up()
            if (res!=None):
                asyncio.create_task(self._custom_data["TwoTabs"].push_on_stack(ErrorWindow(res)))
            return None
        
        return super().keypress(size, key)

    

    def doubleClick():
        pass
    def mouse_event(self, size: tuple[int, int] | tuple[int], event, button: int, col: int, row: int, focus: bool) -> bool | None:
        
        return super().mouse_event(size, event, button, col, row, focus)

