import os
import os.path

from logic.workspacemanager import WorkspaceManager
from logic.permissions import FilePermissions
from logic.subscriptable import Subscriptable

def possiblePermissionError(fun):
    def wrapper(*args,**kwargs):
        try:
            return fun(*args,**kwargs)
        except PermissionError:
            return "***"

    return wrapper
        

class File(Subscriptable):
    _path:str
    _selected:bool

    def __init__(self) -> None:
        super().__init__()
    
    

    @possiblePermissionError
    def getSize(self)->int | None:
        return os.path.getsize(self._path)
    
    
    def getSelected(self)->bool:
        return self._selected

    def setSelected(self,value:bool)->None:
        self._selected=value
        self.send_update()
        

    def get_permissions(self)->list:
        return FilePermissions.perms_from_stat(os.stat(self._path))

    def getFormattedSize(self)->str:
        sz=self.getSize()
        if sz is None:
           return ""
        sfx=["bytes","KB","MB","GB","TB"]
        pos=0
        while sz>=1024:
            sz/=1024
            pos+=1
        return "{:.2f}".format(sz)+" "+sfx[pos]
    
    def isDir(self)->bool:
        return os.path.isdir(self._path)


    def is_executable(self)->bool:
        return os.access(self._path,os.EX_OK)

    @staticmethod
    def fromPath(path:str)->str:
        file=File()
        file._path=path
        file._selected=False
        return file

    def getPath(self)->str:
        return self._path
    def get_name(self)->str:
        return os.path.basename(self._path)
    def get_directory(self)->str:
        return os.path.dirname(self._path)
    
