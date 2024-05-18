from __future__ import annotations
import asyncio
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspacemanager import WorkspaceManager
from logic.transactions.transaction import *


class ChangePermissionTransaction(Transaction):
    def __init__(self, path: str, old_permissions: list, new_permissions: list) -> None:
        self._path = path
        self._old_permissions = old_permissions
        self._new_permissions = new_permissions

    def revert(self) -> Transaction:
        return ChangePermissionTransaction(self._path, self._new_permissions, self._old_permissions)

    async def execute(self, progress_callback: None | Callable = None) -> None | str:
        try:
            os.chmod(self._path, FilePermissions.int_from_perms(
                self._new_permissions))
        except PermissionError:
            return "Operation not permitted"
