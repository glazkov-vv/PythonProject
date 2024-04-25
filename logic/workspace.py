from os import listdir
import os.path
from logic.file import *
from typing import Iterable

from logic.selection import Selection
from logic.subscriptable import Subscriptable


def build_table(path=None)->Iterable[File]:
    return [File.fromPath(os.path.join("" if path is None else path,h)) for h in listdir(path)]


class WorkspaceManager:
    _instances=[]
    def rebuild_all()->None:
        for h in WorkspaceManager._instances:
            h.rebuild()

class Workspace(Subscriptable):
    def __del__(self)->None:
        WorkspaceManager._instances.remove(self)
    def __init__(self,path) -> None:
        super().__init__()
        self._path=path
        self.rebuild()
        WorkspaceManager._instances.append(self)
    def rebuild(self)->None:
        self._contents=build_table(self.get_path())
        self.send_update()
    def get_contents(self)->Iterable[File]:
        return self._contents
    def get_path(self)->str:
        return self._path
    
    """ def update_view(self)->None:
        if self._callback_object is not None:
            self._callback_object.update_from_top() """

    """ def set_callback_object(self,value:object)->None:
        self._callback_object=value """

    
    def step_in(self,path)->None|str:
        if (not os.access(path,os.R_OK)):
            return "Insufficient permissions to read the directory"

        self._path=path
        self.rebuild()
        self.send_update()
    
    def step_up(self)->None|str:
        return self.step_in(os.path.dirname(self._path))
        
        
    def get_selection(self)->Selection:
        return Selection([h.getPath() for h in self._contents if h.getSelected()])
        