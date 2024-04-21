from __future__ import annotations



class Manager:
    _locked_on=0
    current_two_tabs=None

    @classmethod
    def get_lock(cls)->None|int:
        return cls._locked_on
    
    @classmethod
    def set_lock(cls,value:int|None)->None:
        cls._locked_on=value
        if (value!=None):
            cls.current_two_tabs.amend_focus(value)