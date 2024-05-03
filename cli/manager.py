from __future__ import annotations
from typing import *

from logic.transactions import Transaction
from logic.workspace import Workspace
import urwid

class Manager:
    _locked_on=None
    loop:urwid.MainLoop
    current_two_tabs=None
    active_workspaces:Iterable[Workspace]=[None,None]
    operation_mode:Literal["normal","select_for_move","select_for_copy"]="normal"
    @classmethod
    def get_lock(cls)->None|int:
        return cls._locked_on
    
    @classmethod
    def set_lock(cls,value:int|None)->None:
        cls._locked_on=value
        if (value!=None):
            cls.current_two_tabs.amend_focus(value)

    _queue=[]
    @classmethod
    def push_to_queue(cls,transaction:Transaction)->None:
        cls._queue.append(transaction)
    
    @classmethod
    def pop_from_queue(cls)->Transaction|None:
        if (len(cls._queue)==0):
            return None
        return cls._queue.pop()
    @classmethod
    def global_redraw(cls)->None:
        #cls.current_two_tabs._invalidate()

        cls.loop.screen.clear()
        cls.loop.draw_screen()
