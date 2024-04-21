from __future__ import annotations
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.workspace import WorkspaceManager

class Transaction:
    def __init__(self,path:str) -> None:
        self._path=path
    def execute(self,progress_callback:None|Callable=None)->None:
        raise NotImplementedError()
    def revert(self)->Transaction:
        raise NotImplementedError()

class ChangePermissionTransaction(Transaction):
    def __init__(self,path:str,old_permissions:list,new_permissions:list) -> None:
        super().__init__(path)
        self._old_permissions=old_permissions
        self._new_permissions=new_permissions
    def revert(self) -> Transaction:
        return ChangePermissionTransaction(self._path,self._new_permissions,self._old_permissions)
    def execute(self,progress_callback:None|Callable=None)->None:
        os.chmod(self._path,FilePermissions.int_from_perms(self._new_permissions))

class MoveTransaction(Transaction):
    def __init__(self,path:str,new_path:str) -> None:
        super().__init__(path)
        self._new_path=new_path

    def revert(self)->MoveTransaction:
        return MoveTransaction(self._new_path,self._path)
    
    def execute(self,progress_callback:None|Callable=None)->None:
        shutil.move(self._path,self._new_path)
        WorkspaceManager.rebuild_all()
        