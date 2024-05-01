import os
import os.path

import humanize.time
from datetime import datetime

from logic.workspacemanager import WorkspaceManager
from logic.permissions import FilePermissions
from logic.subscriptable import Subscriptable
import humanize


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
        return humanize.naturalsize(self.getSize())
    
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
    
    def get_modified(self)->datetime:
        return datetime.fromtimestamp(int(os.path.getmtime(self._path)))

    def get_modified_formatted(self)->str:
        return humanize.naturaltime(self.get_modified())

    props={"name":get_name,"size":getSize,"modified":get_modified}
