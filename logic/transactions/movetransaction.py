from __future__ import annotations
import asyncio
import os
import shutil
from typing import *
from logic.permissions import FilePermissions
from logic.selection import Selection
from logic.workspacemanager import WorkspaceManager
from logic.transactions.transaction import *


class MoveTransaction(Transaction):
    @staticmethod
    def reports_progress() -> bool:
        return True

    def __init__(self, files: Selection, new_path: str) -> None:
        def prep(val: str) -> tuple[str, str]:
            return (val, os.path.join(new_path, os.path.basename(val)))

        self._instructions = [prep(h) for h in files.get_list()]
        self._progress_callback = None

    @staticmethod
    def _from_instructions(instructions: list) -> MoveTransaction:
        ans = MoveTransaction.__new__(MoveTransaction)
        ans._instructions = instructions
        return ans

    def set_callback(self, callback: Callable) -> None:
        self._progress_callback = callback

    async def execute(self, progress_callback: None | Callable[..., Any] = None) -> None | str:
        for h in self._instructions:
            if (os.path.exists(h[1])):
                return f"File {h[1]} already exists"
            if (not os.access(os.path.dirname(h[1]), os.W_OK)):
                return f"Cannot create file {h[1]}"
            if (not os.access(h[0], os.W_OK)):
                return f"Cannot move file {h[0]}"

        total_size = calc_total_size([h[0] for h in self._instructions])

        def real_op():
            for h in self._instructions:
                shutil.move(h[0], h[1])

        async def reports(cancellation: asyncio.Event) -> None:
            while True:
                if (cancellation.is_set()):
                    return
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

    def revert(self) -> MoveTransaction:
        return MoveTransaction._from_instructions([(h[1], h[0]) for h in self._instructions])


class MoveSingleTransaction(MoveTransaction):
    def __init__(self, path: str, new_path: str) -> None:
        self._instructions = MoveTransaction._from_instructions(
            [(path, new_path)])._instructions
