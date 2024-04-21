from __future__ import annotations
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspace import WorkspaceManager

class Transaction:
    def __init__(self) -> None:
        pass
    def execute(self,progress_callback:None|Callable=None)->None|str:
        raise NotImplementedError()
    def revert(self)->Transaction:
        raise NotImplementedError()

class ChangePermissionTransaction(Transaction):
    def __init__(self,path:str,old_permissions:list,new_permissions:list) -> None:
        self._path=path
        self._old_permissions=old_permissions
        self._new_permissions=new_permissions
    def revert(self) -> Transaction:
        return ChangePermissionTransaction(self._path,self._new_permissions,self._old_permissions)
    def execute(self,progress_callback:None|Callable=None)->None|str:
        try:
            os.chmod(self._path,FilePermissions.int_from_perms(self._new_permissions))
        except PermissionError:
            return "Operation not permitted"
            

class MoveSingleTransaction(Transaction):
    def __init__(self,path:str,new_path:str) -> None:
        self._path=path
        self._new_path=new_path

    def revert(self)->MoveSingleTransaction:
        return MoveSingleTransaction(self._new_path,self._path)
    
    def execute(self,progress_callback:None|Callable=None)->None|str:
        shutil.move(self._path,self._new_path)
        WorkspaceManager.rebuild_all()
    

class MoveTransaction(Transaction):
    def __init__(self, files:Selection,new_path: str) -> None:
        def prep(val:str)->tuple[str,str]:
            return (val,os.path.join(new_path,os.path.basename(val)))
        
        self._instructions=[prep(h) for h in files.get_list()]


    def execute(self, progress_callback: None | Callable[..., Any] = None) -> None | str:
        for h in self._instructions:
            if (os.path.exists(h[1])):
                return f"File {h[1]} already exists"
            if (not os.access(os.path.dirname(h[1]),os.W_OK)):
                return f"Cannot create file {h[1]}"
            if (not os.access(h[0],os.R_OK)):
                return f"Cannot read file {h[0]}"
        
        for h in self._instructions:
            shutil.move(h[0],h[1])
        WorkspaceManager.rebuild_all()

    def reversed(self)->MoveTransaction:
        return MoveTransaction([(h[1],h[0]) for h in self._instructions])
    

class CopyTransaction(Transaction):
    def __init__(self, files:Selection,new_path: str) -> None:
        def prep(val:str)->tuple[str,str]:
            return (val,os.path.join(new_path,os.path.basename(val)))
        
        self._instructions=[prep(h) for h in files.get_list()]


    def execute(self, progress_callback: None | Callable[..., Any] = None) -> None | str:
        for h in self._instructions:
            if (os.path.exists(h[1])):
                return f"File {h[1]} already exists"
            if (not os.access(os.path.dirname(h[1]),os.W_OK)):
                return f"Cannot create file {h[1]}"
            if (not os.access(h[0],os.R_OK)):
                return f"Cannot read file {h[0]}"
        
        for h in self._instructions:
            shutil.copy(h[0],h[1])
        WorkspaceManager.rebuild_all()

    def reversed(self)->CopyTransaction:
        return CopyTransaction([(h[1],h[0]) for h in self._instructions])