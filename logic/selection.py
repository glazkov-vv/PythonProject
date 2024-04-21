from typing import Iterable

from logic.file import File
class Selection:
    
    def __init__(self,data:list[str]) -> None:
        self._pathes=data
        
    def empty(self)->bool:
        return len(self._pathes)==0
    def get_list(self)->list[str]:
        return self._pathes