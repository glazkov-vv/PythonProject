from os import listdir
import os.path
from logic.file import *
from typing import Iterable

def build_table(path=None)->Iterable[File]:
    return [File.fromPath(os.path.join("" if path is None else path,h)) for h in listdir(path)]


class Workspace:
    def __init__(self,path,callback:object|None=None) -> None:
        self._path=path
        self.rebuild()
        self._callback_object=callback
    def rebuild(self)->None:
        self._contents=build_table(self.get_path())
    def get_contents(self)->Iterable[File]:
        return self._contents
    def get_path(self)->str:
        return self._path
    def update_view(self)->None:
        if self._callback_object is not None:
            self._callback_object.update_from_top()

    def set_callback_object(self,value:object)->None:
        self._callback_object=value

    def step_up(self)->None:
        self._path=os.path.dirname(self._path)
        self.rebuild()
        self.update_view()
    def step_in(self,path)->None:
        self._path=path
        self.rebuild()
        self.update_view()
    