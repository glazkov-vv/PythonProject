from __future__ import annotations
from typing import *

from logic.workspace import Workspace


class Manager:
    _locked_on=None
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