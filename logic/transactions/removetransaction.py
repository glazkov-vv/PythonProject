from __future__ import annotations
import asyncio
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspacemanager import WorkspaceManager
from logic.transactions.transaction import *


class RemoveTransaction(Transaction):
    def __init__(self, files: Selection) -> None:
        self._files = files.get_list()
        super().__init__()

    async def execute(self, progress_callback: None |
                      Callable[..., Any] = None) -> None | str:
        if len(self._files) == 0:
            return "No files selected for removal"
        for h in self._files:
            if not os.path.exists(h):
                return f"File {h} does not exist"
            if (not os.access(os.path.dirname(h), os.W_OK) or not os.access(
                    os.path.dirname(h), os.X_OK) or (os.path.isdir(h) and not os.access(h, os.X_OK))):
                return f"Cannot delete file {h}"

        for h in self._files:
            if os.path.isdir(h):
                shutil.rmtree(h)
            else:
                os.remove(h)
        WorkspaceManager.rebuild_all()

    def revert(self) -> DoNothingTransaction:
        return DoNothingTransaction()
