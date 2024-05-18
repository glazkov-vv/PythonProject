from __future__ import annotations
import asyncio
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspacemanager import WorkspaceManager
from logic.transactions.transaction import *
from logic.transactions.removetransaction import *


class MakeDirectoryTransaction(Transaction):

    def get_name(self):
        yield "Folder"
        i = 0
        while True:
            yield "Folder "+str(i)
            i += 1

    def __init__(self, path) -> None:
        self._path = path
        super().__init__()

    async def execute(self) -> asyncio.Coroutine[asyncio.Any, asyncio.Any, None | str]:
        if (not os.access(self._path, os.W_OK)):
            return f"Can't write to {self._path}"
        for h in self.get_name():
            if (not os.path.exists(os.path.join(self._path, h))):
                os.mkdir(os.path.join(self._path, h))
                WorkspaceManager.rebuild_all()
                self._new_path = os.path.join(self._path, h)
                return

    def revert(self) -> str:

        return RemoveTransaction(Selection([self._new_path]))
