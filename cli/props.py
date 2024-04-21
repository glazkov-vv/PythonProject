from typing_extensions import Literal
import urwid
from cli.stackedview import StackedView
from logic.file import *
from logic.transactions import ChangePermissionTransaction, MoveTransaction




class PropertyWindow(urwid.Widget,StackedView):
    def __init__(self,file:File) -> None:
        super().__init__()
        self._file=file
        self._name_edit=urwid.Edit(file.get_name())
        name=urwid.AttrMap(self._name_edit,None,"reversed")

        sep1=urwid.Divider("-")
        btn_rows=[]
        roles=["User","Group","Others"]
        actions=["Read","Write","Execute"]

        permissions_values=file.get_permissions()

        self._init_permissions=permissions_values
        self._init_name=file.get_name()
        self._permissions_table=[]
        for i in range(3):
            in_btns=[urwid.Text(roles[i])]
            for j in range(3):
                num=3*i+j
                self._permissions_table.append(urwid.CheckBox(actions[j],permissions_values[num]))
                in_btns.append(self._permissions_table[-1])
            
            
            btn_rows.append(urwid.Columns(in_btns))

        
        pile=urwid.Filler(urwid.Pile([name,sep1,*btn_rows]))
        self._content=pile

        self.focus=None
        
    _selectable=True

    def selectable(self)->bool:
        return True

    def rows(self, size: tuple[int], focus: bool = False) -> int:
        return 1
    
    focus=None

    def render(self, size: tuple[()] | tuple[int] | tuple[int, int], focus: bool = False) -> urwid.Canvas:
        
        return self._content.render(size,focus)
    
    def mouse_event(self, size: tuple[()] | tuple[int] | tuple[int, int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
        return self._content.mouse_event(size, event, button, col, row, focus)
    
    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if (key=="esc"):
            self.pop_on_stack()
        if (key=="enter"):
            self.apply()
        val= self._content.keypress(size, key)
        return val
    
    def get_name(self)->str:
        return self._name_edit.get_edit_text()
    
    def get_permissions(self)->list:
        ans=[None]*9
        for i in range(9):
            ans[i]=self._permissions_table[i].get_state()
        return ans

    def apply(self)->None:

        if (self.get_permissions()!=self._init_permissions):
            t1=ChangePermissionTransaction(self._file.getPath(),self._init_permissions,self.get_permissions())
            t1.execute()
        if (self.get_name()!=self._init_name):
            t2=MoveTransaction(self._file.getPath(),os.path.join(self._file.get_directory(),self.get_name()))
            t2.execute()
            
        self.pop_on_stack()
    
class PropertyWindowMock(urwid.Filler,StackedView):
    def __init__(self) -> None:
        super().__init__(urwid.Pile([urwid.Edit()]))
