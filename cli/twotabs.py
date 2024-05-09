import asyncio
import urwid
from cli.error import ErrorWindow
from cli.executestransactions import ExecutesTransactions
from cli.manager import Manager
from cli.stackedview import StackedView
from logic.file import *
from logic.transactions import CopyTransaction, MakeDirectoryTransaction
from logic.workspace import *
from cli.filepanel import *


class TwoTabs(urwid.WidgetContainerMixin, urwid.Widget, ExecutesTransactions):
    _selectable = False

    def selectable(self) -> bool:
        return True

    def __init__(self, custom_data, active_workspaces) -> None:
        super().__init__()

        Manager.current_two_tabs = self
        self._updated_event = asyncio.Event()

        self._custom_data = custom_data
        self._custom_data["viewstack_push_function"] = self.push_on_stack
        self._custom_data["TwoTabs"] = self

        left = FilePanel(self._custom_data, active_workspaces[0], 0)
        right = FilePanel(self._custom_data, active_workspaces[1], 1)
        active_workspaces[0].subscribe(left.rebuild)
        active_workspaces[1].subscribe(right.rebuild)
        # right=build_list(build_table("/"))
        res = urwid.Columns([left, right], dividechars=3)
        self.contents = [(res, None)]

    def rebuild(self) -> None:
        for i in [0, 1]:
            self.contents[0][0].contents[i][0].rebuild()

    def triggerFocusChange(self) -> bool:
        self.contents[0][0].focus_position ^= 1
        return True

    def amend_focus(self, pos: int) -> None:
        self.contents[0][0].focus_position = pos

    def get_focus(self) -> int:
        return self.contents[0][0].focus_position

    async def mkdir(self, path: str) -> None:
        tr = MakeDirectoryTransaction(path)
        await self.execute_transaction(tr)

    def set_normal_mode(self):
        Manager.set_lock(None)
        Manager.operation_mode = "normal"

    async def paste(self):
        Transaction = MoveTransaction if Manager.operation_mode == "select_for_move" else CopyTransaction
        transaction = Transaction(
            Manager.active_selection, Manager.active_workspaces[Manager.get_lock()].get_path())
        await self.execute_transaction(transaction)
        self.set_normal_mode()

    def keypress(self, size: tuple[()] | tuple[int] | tuple[int, int], key: str) -> str | None:
        if (key == "z"):
            if (Manager.operation_mode == "normal"):
                val = Manager.pop_from_queue()
                if (val != None):
                    asyncio.create_task(self.execute_transaction(val, True))

                return None
        if (key == "esc" and Manager.operation_mode != 'normal'):
            self.set_normal_mode()
            return None

        if (key == 'f5'):
            if (Manager.operation_mode == "normal"):
                for h in Manager.active_workspaces:
                    h.rebuild()
                return None
        if (key == 'v'):
            if (Manager.get_lock() != None):
                asyncio.create_task(self.paste())
            return None
        if key == 'tab':
            if (Manager.get_lock() == None):
                self.contents[0][0].focus_position ^= 1
            return None

        return self.contents[0][0].focus.keypress(size, key)

    def mouse_event(self, size: tuple[()] | tuple[int] | tuple[int, int], event: str, button: int, col: int, row: int, focus: bool) -> bool | None:
        if (Manager.operation_mode == "normal"):
            return self.contents[0][0].mouse_event(size, event, button, col, row, True)
        else:
            lck = Manager.get_lock()
            return self.contents[0][0].contents[lck][0].mouse_event(size, event, button, col, row, True)

    def render(self, size: tuple[int, int], focus: bool = False) -> urwid.Canvas:
        (maxcol, maxrow) = size

        return self.contents[0][0].render(size, focus)

    def _invalidate(self) -> None:
        for h in self.contents:
            h[0]._invalidate()
        return super()._invalidate()
    """ def update(self,path,num)->None:
        active_workspaces[num]=Workspace(path)
        self.contents[0][0].contents[num]=(FilePanel(active_workspaces[num],num),self.contents[0][0].contents[num][1])
        self._invalidate() """
