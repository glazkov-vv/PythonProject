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


class CopyTransaction(Transaction):

    @staticmethod
    def reports_progress() -> bool:
        return True

    def __init__(self, files: Selection, new_path: str) -> None:
        def prep(val: str) -> tuple[str, str]:
            return (val, os.path.join(new_path, os.path.basename(val)))
        self._progress_callback = None
        self._instructions = [prep(h) for h in files.get_list()]

    def set_callback(self, callback: Callable) -> None:
        self._progress_callback = callback

    @staticmethod
    def _from_instructions(instructions: list) -> CopyTransaction:
        ans = CopyTransaction.__new__(CopyTransaction)
        ans._instructions = instructions
        return ans

    async def execute(self) -> None | str:
        for source, dest in self._instructions:
            if (os.path.exists(dest)):
                return f"File {dest} already exists"
            if (not os.access(os.path.dirname(dest), os.W_OK)):
                return f"Cannot create file {dest}"
            if (not os.access(source, os.R_OK)):
                return f"Cannot read file {source}"

            if (os.path.isdir(source)):
                walkres = None
                try:
                    walkres = os.walk(source)
                except:
                    return f"Permission error while traversing directory {source}"
                for curdir, subdirs, subfiles in walkres:
                    for hhh in subdirs+subfiles:
                        if (not os.access(os.path.join(curdir, hhh), os.R_OK)):
                            return f"Cannot read file {hhh} from {source}"

        total_size = calc_total_size([source for h in self._instructions])

        def real_op():
            i = 0
            for h in self._instructions:
                if (os.path.isdir(source)):
                    shutil.copytree(source, dest)
                else:
                    shutil.copy(source, dest)

        async def reports(cancellation: asyncio.Event) -> None:
            while not cancellation.is_set():
                cur_size = calc_total_size([h[1] for h in self._instructions])
                share = cur_size/total_size if total_size != 0 else 1
                if (self._progress_callback != None):
                    self._progress_callback(share)
                await asyncio.sleep(0.2)

        cancel_reports = asyncio.Event()
        asyncio.create_task(reports(cancel_reports))
        await asyncio.to_thread(real_op)
        cancel_reports.set()
        WorkspaceManager.rebuild_all()

    def revert(self) -> CopyTransaction:
        return RemoveTransaction(Selection([h[1] for h in self._instructions]))
